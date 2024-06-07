# Change log
&nbsp;
## 1.3.0
&nbsp;
### NEW
- sorting and grouping now possible based on CRS
- additional action to expand/collapse groups on double click
- snapshots directory can now be set (defaults to /Snapshots inside plugin directory)
- settings for snapshots directory and expanding groups option are saved between sessions
<!-- -->
&nbsp;
### FIXED
&nbsp;
- when copying layer files, if a file contained multiple dots in its name, the extension(s) would be doubled
- snapshot loading misreporting layers failed to load when copying vector layers to memory
- CRS not being applied to layers containing non EPSG authority CRS when loading snapshots 
- sort and group dialog won't be rebuilt every time it is opened
- snapshots dialog won't be rebuilt every time it is opened
- feature count not working when sorting lowest to highest due to change of GUI element name
- grouping by name failing due to parsing of wrong parameters
<!-- -->
&nbsp;
## 1.2.1
&nbsp;
### NEW
&nbsp;
- added option to sort layers by name using alphabetical or natural sorting
- added additional action to copy layers files to new directory
- additional actions menu also available from the plugin button in plugins toolbar
- added option to group nodes by regex pattern (node name)
<!-- -->
&nbsp;  
### FIXED
&nbsp;
- using 'extract all and sort in root' would disregard the final encountered group and layers in it would be lost
- background processing not working on some systems (getting garbage collected before execution)
<!-- -->
&nbsp;  
### CHANGED
&nbsp;
- file size is calculated from QGIS reported sidecar files
<!-- -->
&nbsp;
## 1.1
&nbsp;  
###  NEW
&nbsp;  
- layer symbology is now automatically saved in snapshot file and applied on reloading  
    + snapshots made with the previous version can be loaded with the new version  
    + snapshots made with the current version can be loaded with the old version  
<!-- -->
&nbsp;  
- added icons to layers panel
    + shortcut for Sort and group
    + shortcut for Snapshot
    + additional actions
        - commit changes to layers
        - reload layers
        - toggle feature count
        - truncate (delete features in layers)
<!-- -->
&nbsp;   
- help (README) file added to plugin dropdown menu   
<!-- -->
&nbsp;  
### FIXED
&nbsp;
- when using 'in selected group(s)' option, an error could arose if both a group and its sub-group were selected
    + group order is checked before performing any operations, so it is safe to use the function in any combination
- snapshot creation failing on some Linux distributions due to 'finished' signal never being called to dump file to disk
- replace tree with the snapshot now works