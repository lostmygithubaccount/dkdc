# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Run batch of AutoML experiments on multiple data sets."""

import os
import time
import errno
import shutil
import logging
import argparse

import numpy as np
import pandas as pd

from sklearn.metrics import accuracy_score

import azureml.core
from azureml import dataprep
from azureml.train.automl import AutoMLConfig
from azureml.core.workspace import Workspace
from azureml.core.experiment import Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.conda_dependencies import CondaDependencies

DATASETS = [
    'ag_news',
    'DogBreeds_vs_Fruits',
    'DBPedia',
    'Amazon_reviews_cleaned_20K',
    'Sentiment_amazon',
    'Sentiment_imdb',
    'Sentiment_yelp',
    'newsgroups_small',
    'semeval_small',
    'newsgroups',
    'semeval',
]
TARGET_INDICES = {
    'ag_news': 1,
    'DogBreeds_vs_Fruits': 0,
    'DBPedia': 0,
    'iris_train': 4,
    'Amazon_reviews_cleaned_20K': 0,
    'Sentiment_amazon': 1,
    'Sentiment_imdb': 2,
    'Sentiment_yelp': 2,
    'newsgroups_small': 2,
    'semeval_small': 2,
    'newsgroups': 2,
    'semeval': 2,
}
FEATURE_INDICES = {
    'ag_news': [2],
    'DogBreeds_vs_Fruits': [1],
    'DBPedia': [2],
    'iris_train': [0, 1, 2, 3],
    'Amazon_reviews_cleaned_20K': [1],
    'Sentiment_amazon': [0],
    'Sentiment_imdb': [1],
    'Sentiment_yelp': [1],
    'newsgroups_small': [1],
    'semeval_small': [1],
    'newsgroups': [1],
    'semeval': [1],
}
LARGE_DATASETS_WITH_VAL_SET = ['ag_news', 'DBPedia',
                               'DogBreeds_vs_Fruits']


def get_workspace_config(workspace):
    """Get AutoML workspace configuration"""
    config = {}
    config['SDK version'] = azureml.core.VERSION
    config['Subscription ID'] = workspace.subscription_id
    config['Workspace'] = workspace.name
    config['Resource Group'] = workspace.resource_group
    config['Location'] = workspace.location
    pd.set_option('display.max_colwidth', -1)
    return pd.DataFrame(data=config, index=[''])


def read_data(dirpath, dataset, split):
    """Read CSV data from file"""
    data_filename = dataset + '_' + split + '.csv'
    data_filepath = os.path.join(dirpath, dataset, data_filename)

    if not os.path.isfile(data_filepath):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), data_filename)

    try:
        return pd.read_csv(data_filepath)
    except:
        return pd.read_csv(data_filepath, sep='\t')


def sample_train_data(data, max_sample_size=1000000):
    """Prune large data sets by sub-sampling"""
    if data.shape[0] > max_sample_size:
        data = data.sample(n=max_sample_size, random_state=123)
    return data


def prepare_data_for_remote_run(dataset, split, features, labels):
    """Upload dataset to remote and return DataFlow object."""
    # upload the dataset to remote compute.
    if not os.path.isdir('.temp'):
        os.mkdir('.temp')

    suffix = split + '.csv'
    features_fname, labels_fname = '/features_' + suffix, '/labels_' + suffix

    pd.DataFrame(features).to_csv('.temp' + features_fname, index=False)
    pd.DataFrame(labels).to_csv('.temp' + labels_fname, index=False)

    workspace = Workspace.from_config()
    datastore = workspace.get_default_datastore()
    datastore.upload(src_dir='./.temp', target_path=dataset)  # does not overwrite
    shutil.rmtree('.temp')

    # get DataFlow objects
    features = dataprep.read_csv(path=datastore.path(dataset + features_fname), infer_column_types=True)
    labels = dataprep.read_csv(path=datastore.path(dataset + labels_fname), infer_column_types=True)

    return features, labels


def get_data(dirpath, dataset, split, max_sample_size=1000000, remote_run=False):
    """Get sampled text data corresponding to provided data split"""
    data = read_data(dirpath, dataset, split)

    if split == 'train':
        data = sample_train_data(data, max_sample_size)

    features = np.array(data.iloc[:, FEATURE_INDICES[dataset]])
    labels = np.array(data.iloc[:, TARGET_INDICES[dataset]])

    print('Number of examples in "{0}" split of "{1}" dataset = {2}'.format(split, dataset, features.shape[0]))

    if remote_run and split in ['train', 'valid', 'validate']:
        features, labels = prepare_data_for_remote_run(dataset, split, features, labels)

    return features, labels


def get_experiment_results(automl_run, dataset):
    child_runs = list(automl_run.get_children())

    run_attributes = ['run_preprocessor', 'run_algorithm', 'score', 'iteration']
    results = pd.DataFrame([[run.get_properties()[attr] for attr in run_attributes]
                            for run in child_runs],
                           columns=run_attributes).set_index('iteration'
                                                             ).sort_index().reset_index()

    results['dataset'] = dataset
    results.index.name = 'index'
    results.iteration = results.iteration.apply(lambda x: int(x))
    results.sort_values(by=['dataset', 'iteration'], inplace=True)

    # Add max score statistic
    max_score = results['score'].cummax().rename(columns={'score': 'max score'}, inplace=True)
    results = results.join(pd.DataFrame(max_score))

    return results


def write_results(df, filepath, mode):
    """Dump results to CSV file"""
    with open(filepath, mode) as f:
        df.to_csv(f, header=f.tell() == 0)


def get_aml_compute(workspace, cluster_name='cpu-cluster', use_gpu=False):
    """Create or get existing AzureML compute cluster"""
    # Check if compute target already exists in the workspace.
    clusters = workspace.compute_targets
    if cluster_name in clusters and clusters[cluster_name].type == 'AmlCompute':
        print('Found existing compute target.')
        compute_target = clusters[cluster_name]
    else:
        print('Creating a new compute target...')
        vm_size = "STANDARD_D2_V2" if not use_gpu else "STANDARD_NC6"
        provisioning_config = AmlCompute.provisioning_configuration(vm_size, max_nodes=5)
        compute_target = ComputeTarget.create(workspace, cluster_name, provisioning_config)
        compute_target.wait_for_completion(show_output=True)

    return compute_target


def configure_remote_runtime(compute_target, build_name, build_id, use_gpu=False):
    """Attach remote compute and """
    # create a new RunConfiguration object
    conda_run_config = RunConfiguration(framework="python")

    # set compute target to AmlCompute
    conda_run_config.target = compute_target
    conda_run_config.environment.docker.enabled = True
    conda_run_config.environment.docker.base_image = azureml.core.runconfig.DEFAULT_CPU_IMAGE \
        if not use_gpu else azureml.core.runconfig.DEFAULT_GPU_IMAGE

    # install SDK
    conda_deps = CondaDependencies.create(pip_packages=['azureml-sdk[automl]'])
    conda_deps.add_pip_package('azureml-sdk[automl]<0.1.1')
    conda_deps.set_pip_option(
        '--extra-index-url https://azuremlsdktestpypi.azureedge.net/{}/{}'.format(build_name, build_id))
    conda_run_config.environment.python.conda_dependencies = conda_deps

    return conda_run_config


def main(args):
    # get AutoML workspace
    workspace = Workspace.from_config()
    print(get_workspace_config(workspace).T, '\n')

    for dataset in args.datasets:
        experiment_name = args.tag + '-' + dataset
        experiment = Experiment(workspace, experiment_name[:36])  # max 36 characters allowed
        print('Running experiment "{}" on data set "{}"'.format(experiment_name, dataset))

        log_dirpath = os.path.join(args.project_dirpath, 'log')
        if not os.path.isdir(log_dirpath):
            os.mkdir(log_dirpath)
        automl_log_filepath = os.path.join(log_dirpath, experiment_name + '.log')

        # get train, test, validation data splits
        x_train, y_train = get_data(args.data_dirpath, dataset, 'train', args.max_sample_size, args.remote_run)
        x_test, y_test = get_data(args.data_dirpath, dataset, 'test')
        x_valid = None

        if x_train.shape[0] > 10000 and dataset in LARGE_DATASETS_WITH_VAL_SET \
                or args.enforce_val_set:
            for split in ['valid', 'validate']:
                try:
                    x_valid, y_valid = get_data(args.data_dirpath, dataset, split, remote_run=args.remote_run)
                except FileNotFoundError:
                    continue
            if x_valid is None:
                print("Validation data for {} was not found. Skipping data set.".format(dataset))
                continue
            validation_settings = {'X_valid': x_valid, 'y_valid': y_valid}
            print('Using val set for validation.')
        else:
            validation_settings = {'n_cross_validations': args.k_folds_cv}
            print('Using ' + str(args.k_folds_cv) + '-fold CV for validation.')

        # configure automl experiment
        automl_settings = {
            'primary_metric': 'accuracy',
            'iteration_timeout_minutes': 60,
            'iterations': args.iterations,
            'verbosity': logging.INFO,
            'preprocess': True,
        }

        if args.remote_run:
            compute_target = get_aml_compute(workspace, args.cluster_name, args.use_gpu)
            automl_settings['run_configuration'] = \
                configure_remote_runtime(compute_target, args.build_name, args.build_id, args.use_gpu)

        automl_config = AutoMLConfig(
            task='classification',
            name=experiment_name,
            debug_log=automl_log_filepath,
            X=x_train,
            y=y_train,
            path=args.project_dirpath,
            **validation_settings,
            **automl_settings,
        )

        # run experiment for each data set
        automl_run = experiment.submit(automl_config, show_output=True)
        results = get_experiment_results(automl_run, dataset)

        # dump results to CSV
        mode = 'a' if args.append else 'w'
        write_results(results, args.results_filepath, mode)

        # Evaluate on test set
        best_run, fitted_model = automl_run.get_output()
        predicted = fitted_model.predict(x_test)
        test_accuracy = accuracy_score(predicted, y_test)
        print('Test Accuracy = {}.\n'.format(test_accuracy))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run batch of AutoML experiments')
    parser.add_argument('--data', dest='datasets', nargs='+',
                        default=['DogBreeds_vs_Fruits'], help='List of data sets or "all"')

    # configure project and data directory
    curr_dir, home_dir = os.getcwd(), os.path.expanduser("~")
    parser.add_argument('--project-dirpath', default=curr_dir)
    parser.add_argument('--data-dirpath', default=os.path.join(home_dir, 'data'))
    parser.add_argument('--results-filepath', type=str)

    # number of iterations for model selection
    parser.add_argument('-i', '--iterations', type=int, default=3,
                        help='Number of iterations for model selection')
    # prune large training data sets
    parser.add_argument('--max-sample-size', type=int, default=1000000,
                        help='Number of instances to sample from dataset')

    # validation hyper-parameters
    cross_val_parser = parser.add_mutually_exclusive_group(required=False)
    cross_val_parser.add_argument('-k', '--k-folds-cv', type=int, default=5,
                                  help='Number of cross-fold validation')
    cross_val_parser.add_argument('--enforce-val-set', action='store_true',
                                  help='Enforce validation set on all data sets')
    parser.set_defaults(enforce_val_set=False)

    # tag experiment
    curr_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
    parser.add_argument('--tag', default=curr_time,
                        help='Tag to name your experiment')

    # configure aml compute cluster
    parser.add_argument('--cluster-name', type=str, default='cpu-cluster',
                        help='Cluster name for Azure remote compute')
    parser.add_argument('--gpu', action='store_true', dest='use_gpu')

    # configure local/ remote runs
    runtime_env_parser = parser.add_mutually_exclusive_group(required=False)
    runtime_env_parser.add_argument('-r', '--remote',
                                    dest='remote_run', action='store_true')
    runtime_env_parser.add_argument('-l', '--local',
                                    dest='remote_run', action='store_false')
    parser.set_defaults(remote_run=False)

    # configure pypi build for remote runs
    parser.add_argument('--build-name', type=str, default='AzureML-Train-AutoML-Validation')
    parser.add_argument('--build-id', type=str, default='4857542')  # 4863685

    # create/append results to csv file dump
    parser.add_argument('-a', '--append', action='store_true',
                        help='Create or append to log file')

    parsed_args = parser.parse_args()

    # configure list of datasets and results CSV filepath
    if 'all' in parsed_args.datasets:
        parsed_args.datasets = DATASETS

    # create project directory, if it does not exist
    if not os.path.isdir(parsed_args.project_dirpath):
        os.mkdir(parsed_args.project_dirpath)

    if parsed_args.results_filepath is None:
        results_dirpath = os.path.join(curr_dir, 'out')
        if not os.path.isdir(results_dirpath):
            os.mkdir(results_dirpath)
        parsed_args.results_filepath = os.path.join(results_dirpath,
                                                    parsed_args.tag + '.csv')

    # always append to results file if tag is not specified
    if parsed_args.tag == curr_time:
        parsed_args.append = True

    main(parsed_args)
