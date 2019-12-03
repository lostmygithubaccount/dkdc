# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Custom Torchvision Dataset class."""

exception_string = ''
import_error = False

try:
    import torch
    import io

    from PIL import Image
except ImportError as e:
    import_error = True
    exception_string = str(e)

if not import_error:
    class _TorchvisionObjectDetectionDataset(torch.utils.data.Dataset):
        def __init__(self, dataflow, image_url_column, transform=None, target_transform=None):
            self._dataflow = dataflow
            self._image_url_column = image_url_column
            self._image_meta = dataflow.to_pandas_dataframe(extended_types=True)
            self._len = self._image_meta.shape[0]
            self.no_of_labels = 0
            self.transform = transform
            self.target_transform = target_transform
            self.labels_to_numbers = {}

        def __getitem__(self, idx):
            image = self._image_meta.iloc[idx]
            dataflow = self._dataflow

            if idx != 0:
                dataflow = dataflow.skip(idx).take(1)
            else:
                dataflow = dataflow.take(1)

            dataflow = dataflow.keep_columns(self._image_url_column) \
                               .rename_columns({self._image_url_column: 'Path'}) \
                               .add_step('Microsoft.DPrep.ReadStreamBlock', {'maxBytes': 104857600})  # 100 Mb
            image_raw = dataflow.to_pandas_dataframe(extended_types=True)
            binary_content = image_raw.iloc[0].Contents
            file_object = io.BytesIO(binary_content)
            img = Image.open(file_object).convert("RGB")
            width, height = img.size

            num_objects = 1
            if isinstance(image.label, list):
                num_objects = len(image.label)

            boxes = []
            object_labels = []
            iscrowd_list = []
            for i in range(num_objects):
                if isinstance(image.label, list):
                    label_object = image.label[i]
                else:
                    label_object = image.label

                xmin = float(label_object['topX']) * width
                ymin = float(label_object['topY']) * height
                xmax = float(label_object['bottomX']) * width
                ymax = float(label_object['bottomY']) * height

                if xmin > xmax:
                    xmin, xmax = xmax, xmin

                if ymin > ymax:
                    ymin, ymax = ymax, ymin

                boxes.append([xmin, ymin, xmax, ymax])
                label_str = label_object['label']
                label_number = self.labels_to_numbers.get(label_str)

                if label_number:
                    object_labels.append(label_number)
                else:
                    self.no_of_labels += 1
                    object_labels.append(self.no_of_labels)
                    self.labels_to_numbers[label_str] = self.no_of_labels

                if 'isCrowd' in label_object:
                    iscrowd_list.append(1 if label_object['isCrowd'] == 'true' else 0)
                else:
                    iscrowd_list.append(0)

            image_id = torch.as_tensor([idx])
            boxes = torch.as_tensor(boxes, dtype=torch.float32)
            area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
            iscrowd = torch.as_tensor(iscrowd_list, dtype=torch.int64)
            labels = torch.as_tensor(object_labels, dtype=torch.int64)

            target = {}
            target["boxes"] = boxes
            target["labels"] = labels
            target["image_id"] = image_id
            target["area"] = area
            target["iscrowd"] = iscrowd

            if self.transform is not None:
                img = self.transform(img)

            if self.target_transform is not None:
                target = self.target_transform(target)

            return img, target

        def __len__(self):
            return self._len

    class _TorchvisionImageClassificationDataset(torch.utils.data.Dataset):
        def __init__(self, dataflow, image_url_column, transform=None, target_transform=None):
            self._dataflow = dataflow
            self._image_url_column = image_url_column
            self._image_meta = dataflow.to_pandas_dataframe(extended_types=True)
            self._len = self._image_meta.shape[0]
            self.transform = transform
            self.target_transform = target_transform
            self.labels = {}
            self.label_index = 0

        def __getitem__(self, idx):
            image = self._image_meta.iloc[idx]
            dataflow = self._dataflow

            if idx != 0:
                dataflow = dataflow.skip(idx).take(1)
            else:
                dataflow = dataflow.take(1)

            dataflow = dataflow.keep_columns(self._image_url_column) \
                               .rename_columns({self._image_url_column: 'Path'}) \
                               .add_step('Microsoft.DPrep.ReadStreamBlock', {'maxBytes': 104857600})  # 100 Mb
            image_raw = dataflow.to_pandas_dataframe(extended_types=True)
            binary_content = image_raw.iloc[0].Contents
            file_object = io.BytesIO(binary_content)
            pil_img = Image.open(file_object).convert("RGB")
            target = None

            if isinstance(image.label, str):
                label_number = self.labels.get(image.label)
                if label_number:
                    target = label_number
                else:
                    self.label_index += 1
                    self.labels[image.label] = self.label_index
                    target = self.label_index
            elif isinstance(image.label, list):
                target = []
                for label_string in image.label:
                    label_number = self.labels.get(label_string)
                    if label_number:
                        target.append(label_number)
                    else:
                        self.label_index += 1
                        self.labels[label_string] = self.label_index
                        target.append(self.label_index)

            if self.transform is not None:
                pil_img = self.transform(pil_img)

            if self.target_transform is not None:
                target = self.target_transform(target)

            return pil_img, target

        def __len__(self):
            return self._len

        def _get_classes(self):
            return self.labels
