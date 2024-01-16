# Change log
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
    + group order is checked before performing any operations, so it safe to use the function in any combination
- snapshot creation failing on some Linux distributions due to 'finished' signal never being called to dump file to disk
- replace tree with the snapshot now works