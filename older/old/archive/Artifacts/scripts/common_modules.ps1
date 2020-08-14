#Returns normalized path
function Resolve-FullPath($path)
{
    $p = Resolve-Path $path
    $p.Path
}

#Badly named funtion to read a json file content
function Get-Target($scenario)
{
    Get-Content -Raw -Path $scenario | ConvertFrom-Json
}

#Convert psObject into Hashtable
function ConvertTo-Hashtable($psObject)
{ 
    $spec = @{}
    foreach ($obj in $psObject.psobject.properties) 
    { 
        if ($obj.Value.GetType().Name -eq "PSCustomObject")
        {
            $spec[$obj.Name] = ConvertTo-Hashtable $obj.Value
        }
        else
        {
            $spec[$obj.Name] = $obj.Value
        }
     } 
     return $spec
}

#release.json specific util to merge nested release.json files into a common config
function Merge-Include($path, $hashTable)
{
    $root = $path
    [System.Collections.ArrayList]$__uploads = @()
    if ($hashTable.uploads)
    {
        foreach ($u in $hashTable.uploads)
        {
            $__uploads.Add([system.io.path]::combine($path, $u))
        }    
    }
    $hashTable.uploads = $__uploads

    if ($hashTable -and $hashTable.include)
    {
        foreach ($h in $hashTable.include.GetEnumerator()) 
        {
            $key = $h.Name

            $newpath = [system.io.path]::combine($path, $h.Value)
            $nbpath = [system.io.path]::combine($newpath, "release.json")

            $raw_include_nb = Get-Target $nbpath
            $ht_include_nb = ConvertTo-Hashtable $raw_include_nb
            $include_nd = Merge-Include $newpath $ht_include_nb

            if ($include_nd.uploads)
            {
                foreach ($u in $include_nd.uploads)
                {
                    $hashTable.uploads.Add($u)
                }
            }

            foreach ($n in $include_nd.notebooks.GetEnumerator())
            {
                $id = $key+"-"+$n.Name
                $n.Value.path=[system.io.path]::Combine($newpath.Substring($root.Length),$n.Value.path).Trim('\')
                $hashTable.notebooks.Add("$id", $n.Value)
            }

            foreach ($chnl in $include_nd.channels.GetEnumerator())
            {
                if ($hashTable.channels.$($chnl.Name))
                {
                     $hashTable.channels.$($chnl.Name) += $chnl.Value | ForEach-Object {"$key-$_"}
                }
                else
                {
                    $hashTable.channels.$($chnl.Name) = $chnl.Value | ForEach-Object {"$key-$_"}
                }
            }

        }
    }

    return $hashTable
}