# Layer Tree Tools (sort, group, snapshot)

## SORTING

Options:
  * root only
    
    Sorts layers and groups in root only.
    
  * order within all groups (root included)

    Sorts layers and groups in all groups, including root.

  * within selected group(s)

    Sorts layers and groups only in selected group(s).  
    Does not sort sub-groups in groups.

  * extract and sort all in root

    Moves all layers to root and sorts them.  
    Groups get deleted.

### NAME

Sorts layers based on their name.

Options:
  * A-Z
  * Z-A

#### NAME SORTING EXAMPLE
<pre>
    
├── SERBIA                
│   ├── Belgrade  
│   ├── Novi Sad  
│   ├── Niš  
│   └── Kragujevac  
└── CROATIA  
    ├── Zagreb  
    ├── Osijek  
    ├── Rijeka  
    └── Split  
  
</pre>

<pre>
  
          root only           .  order within all groups (root included)  .      selected group(s) only    .  extract all and sort in root
                              .                                           .                                .
├── CROATIA                   .  ├── CROATIA                              .  ├── SERBIA                    .  ├── Belgrade
│   ├── Zagreb                .  │   ├── Osijek                           .  │   ├── Belgrade              .  ├── Kragujevac
│   ├── Osijek                .  │   ├── Rijeka                           .  │   ├── Novi Sad              .  ├── Niš
│   ├── Rijeka                .  │   ├── Split                            .  │   ├── Niš                   .  ├── Novi Sad
│   └── Split                 .  │   └── Zagreb                           .  │   └── Kragujevac            .  ├── Osijek
└── SERBIA                    .  └── SERBIA                               .  └── CROATIA (selected group)  .  ├── Rijeka
    ├── Belgrade              .      ├── Belgrade                         .      ├── Osijek                .  ├── Split
    ├── Novi Sad              .      ├── Kragujevac                       .      ├── Rijeka                .  └── Zagreb
    ├── Niš                   .      ├── Niš                              .      ├── Split                 .
    └── Kragujevac            .      └── Novi Sad                         .      └── Zagreb                .

</pre>

### GEOMETRY  

Sorts layers based on their geometry.

__NOTE__: even though RASTERS and GROUPS are not geometry types, they are treated as such when sorting in order to provide the user more flexibility on the type order.

Options:
 * list order of geometries [polygon, line, point, raster, groups]

#### GEOMETRY EXAMPLE

<pre>
  
├── SERBIA
│   ├── Belgrade (polygon)
│   ├── Novi Sad (polygon)
│   ├── Niš (point)
│   └── Kragujevac (point)
├── CROATIA
│   ├── Zagreb (point)
│   ├── Osijek (point)
│   ├── Rijeka (line)
│   └── Split (line)
├── Sarajevo (point)
├── Banja Luka (line)
├── Mostar (polygon)
└── Bosnia and Herzegovina (raster)
  
</pre>

<pre>
  
Order example:
    1.) line
    2.) point
    3.) polygon
    4.) groups
    5.) raster
  
</pre>


<pre>
  
            root only                .  order within all groups (root included)  .          selected group(s) only       .  extract all and sort in root
                                     .                                           .                                       .
├── Banja Luka (line)                .  ├── Banja Luka (line)                    .  ├── SERBIA                           .  ├── Banja Luka (line)
├── Sarajevo (point)                 .  ├── Sarajevo (point)                     .  │   ├── Belgrade (polygon)           .  ├── Rijeka (line)
├── Mostar (polygon)                 .  ├── Mostar (polygon)                     .  │   ├── Novi Sad (polygon)           .  ├── Split (line)
├── SERBIA                           .  ├── SERBIA                               .  │   ├── Niš (point)                  .  ├── Sarajevo (point)
│   ├── Belgrade (polygon)           .  │   ├── Niš (point)                      .  │   └── Kragujevac (point)           .  ├── Niš (point)
│   ├── Novi Sad (polygon)           .  │   ├── Kragujevac (point)               .  ├── CROATIA (selected group)         .  ├── Kragujevac (point)
│   ├── Niš (point)                  .  │   ├── Belgrade (polygon)               .  │   ├── Rijeka (line)                .  ├── Zagreb (point)
│   └── Kragujevac (point)           .  │   └── Novi Sad (polygon)               .  │   ├── Split (line)                 .  ├── Osijek (point)
├── CROATIA                          .  ├── CROATIA                              .  │   ├── Zagreb (point)               .  ├── Mostar (polygon)
│   ├── Zagreb (point)               .  │   ├── Rijeka (line)                    .  │   └── Osijek (point)               .  ├── Belgrade (polygon)
│   ├── Osijek (point)               .  │   ├── Split (line)                     .  ├── Sarajevo (point)                 .  ├── Novi Sad (polygon)
│   ├── Rijeka (line)                .  │   ├── Zagreb (point)                   .  ├── Banja Luka (line)                .  └── Bosnia and Herzegovina (raster)
│   └── Split (line)                 .  │   └── Osijek (point)                   .  ├── Mostar (polygon)                 .
└── Bosnia and Herzegovina (raster)  .  └── Bosnia and Herzegovina (raster)      .  ├── Bosnia and Herzegovina (raster)  .

</pre>

### FEATURE COUNT

Sorts layers based on their feature count. 

Options:
  * highest to lowest
  * lowest to highest

*Only vector layers have feature count.

#### FEATURE COUNT EXAMPLE

<pre>
  
├── SERBIA
│   ├── Belgrade (1,681,405)
│   ├── Novi Sad (368,967)
│   ├── Niš (249,501)
│   └── Kragujevac (171,186)
├── CROATIA
│   ├── Zagreb (769,944)
│   ├── Osijek (96,848)
│   ├── Rijeka (108,622)
│   └── Split (161,312)
├── Sarajevo (275,524)
├── Banja Luka (185,042)
├── Mostar (105,797)
  
</pre>

<pre>

          root only           .  order within all groups (root included)  .    selected group(s) only      .  extract all and sort in root
                              .                                           .                                .
├── Sarajevo (275,524)        .  ├── Sarajevo (275,524)                   .  ├── SERBIA                    .  ├── Belgrade (1,681,405)
├── Banja Luka (185,042)      .  ├── Banja Luka (185,042)                 .  │   ├── Belgrade (1,681,405)  .  ├── Zagreb (769,944)
├── Mostar (105,797)          .  ├── Mostar (105,797)                     .  │   ├── Novi Sad (368,967)    .  ├── Novi Sad (368,967)
├── SERBIA                    .  ├── SERBIA                               .  │   ├── Niš (249,501)         .  ├── Sarajevo (275,524)
│   ├── Belgrade (1,681,405)  .  │   ├── Belgrade (1,681,405)             .  │   └── Kragujevac (171,186)  .  ├── Niš (249,501)
│   ├── Novi Sad (368,967)    .  │   ├── Novi Sad (368,967)               .  ├── CROATIA (selected group)  .  ├── Banja Luka (185,042)
│   ├── Niš (249,501)         .  │   ├── Niš (249,501)                    .  │   ├── Zagreb (769,944)      .  ├── Kragujevac (171,186)
│   └── Kragujevac (171,186)  .  │   └── Kragujevac (171,186)             .  │   ├── Split (161,312)       .  ├── Split (161,312)
├── CROATIA                   .  ├── CROATIA                              .  │   ├── Rijeka (108,622)      .  ├── Rijeka (108,622)
│   ├── Zagreb (769,944)      .  │   ├── Zagreb (769,944)                 .  │   └── Osijek (96,848)       .  ├── Mostar (105,797)
│   ├── Osijek (96,848)       .  │   ├── Split (161,312)                  .  ├── Sarajevo (275,524)        .  ├── Osijek (96,848)
│   ├── Rijeka (108,622)      .  │   ├── Rijeka (108,622)                 .  ├── Banja Luka (185,042)      .
│   └── Split (161,312)       .  │   └── Osijek (96,848)                  .  ├── Mostar (105,797)          .
  
</pre>

### ENCODING

Sorty layers based on their encoding.

Options:
  * list order of all encodings in the layer tree

*Only vector layers have feature count.
**Memory layers don't have encoding and their encoding is reported as 'None' in the list.

#### ENCODING EXAMPLE

 <pre>
     
├── SERBIA
│   ├── Belgrade (UTF-8)
│   ├── Novi Sad (UTF-8)
│   ├── Niš (WINDOWS 1251)
│   └── Kragujevac (UTF-16)
├── CROATIA
│   ├── Zagreb (UTF-32)
│   ├── Split (UTF-32)
│   ├── Rijeka (ISO 8859-1)
│   └── Osijek (UTF-16)
├── Sarajevo (UTF-16)
├── Banja Luka (UTF-32)
├── Mostar (UTF-8)
   
 </pre>

 <pre>
   
Order example:
     1.) UTF-32
     2.) UTF-16
     3.) UTF-8
     4.) WINDOWS 1251
     5.) ISO 8859-1
   
 </pre>

 <pre>

        root only             .  order within all groups (root included)  .       selected group(s) only   .  extract all and sort in root
                              .                                           .
├── Banja Luka (UTF-32)       .  ├── Banja Luka (UTF-32)                  .  ├── SERBIA                    .  ├── Banja Luka (UTF-32)
├── Sarajevo (UTF-16)         .  ├── Sarajevo (UTF-16)                    .  │   ├── Belgrade (UTF-8)      .  ├── Zagreb (UTF-32)
├── Mostar (UTF-8)            .  ├── Mostar (UTF-8)                       .  │   ├── Novi Sad (UTF-8)      .  ├── Split (UTF-32)
├── SERBIA                    .  ├── SERBIA                               .  │   ├── Niš (WINDOWS 1251)    .  ├── Kragujevac (UTF-16)
│   ├── Belgrade (UTF-8)      .  │   ├── Kragujevac (UTF-16)              .  │   └── Kragujevac (UTF-16)   .  ├── Sarajevo (UTF-16)
│   ├── Novi Sad (UTF-8)      .  │   ├── Belgrade (UTF-8)                 .  ├── CROATIA (selected group)  .  ├── Osijek (UTF-16)
│   ├── Niš (WINDOWS 1251)    .  │   ├── Novi Sad (UTF-8)                 .  │   ├── Zagreb (UTF-32)       .  ├── Mostar (UTF-8)
│   └── Kragujevac (UTF-16)   .  │   └── Niš (WINDOWS 1251)               .  │   ├── Split (UTF-32)        .  ├── Belgrade (UTF-8)
├── CROATIA                   .  ├── CROATIA                              .  │   ├── Osijek (UTF-16)       .  ├── Novi Sad (UTF-8)
│   ├── Zagreb (UTF-32)       .  │   ├── Zagreb (UTF-32)                  .  │   └── Rijeka (ISO 8859-1)   .  ├── Niš (WINDOWS 1251)
│   ├── Split (UTF-32)        .  │   ├── Split (UTF-32)                   .  ├── Sarajevo (UTF-16)         .  ├── Rijeka (ISO 8859-1)
│   ├── Rijeka (ISO 8859-1)   .  │   ├── Osijek (UTF-16)                  .  ├── Banja Luka (UTF-32)       .
│   └── Osijek (UTF-16)       .  │   └── Rijeka (ISO 8859-1)              .  ├── Mostar (UTF-8)            .
   
 </pre>      
 
### FILETYPE

Sorts layers based on their extension.

Options:
  * list order of extensions of loaded files in layer tree

*Memory layers don't exist as files on drive and their filetype is reported as 'memory'.

#### FILETYPE EXAMPLE

<pre>
    
├── SERBIA
│   ├── Belgrade.shp
│   ├── Novi Sad.geojson
│   ├── Niš.shp
│   └── Kragujevac.geojson
├── CROATIA
│   ├── Zagreb.tif
│   ├── Split.csv
│   ├── Osijek.tif
│   └── Rijeka.csv
├── Sarajevo.tif
├── Banja Luka.csv
├── Mostar.shp

Order example:
    1.) .tif
    2.) .geojson
    3.) .shp
    4.) .csv
</pre>

<pre>

        root only             .  order within all groups (root included)  .    selected group(s) only      .  extract all and sort in root
                              .                                           .                                .
├── Sarajevo.tif              .  ├── Sarajevo.tif                         .  ├── SERBIA                    .  ├── Sarajevo.tif
├── Mostar.shp                .  ├── Mostar.shp                           .  │   ├── Belgrade.shp          .  ├── Zagreb.tif
├── Banja Luka.csv            .  ├── Banja Luka.csv                       .  │   ├── Novi Sad.geojson      .  ├── Osijek.tif
├── SERBIA                    .  ├── SERBIA                               .  │   ├── Niš.shp               .  ├── Novi Sad.geojson
│   ├── Belgrade.shp          .  │   ├── Novi Sad.geojson                 .  │   └── Kragujevac.geojson    .  ├── Kragujevac.geojson
│   ├── Novi Sad.geojson      .  │   ├── Kragujevac.geojson               .  ├── CROATIA (selected group)  .  ├── Mostar.shp
│   ├── Niš.shp               .  │   ├── Belgrade.shp                     .  │   ├── Zagreb.tif            .  ├── Belgrade.shp
│   └── Kragujevac.geojson    .  │   └── Niš.shp                          .  │   ├── Osijek.tif            .  ├── Niš.shp
├── CROATIA                   .  ├── CROATIA                              .  │   ├── Split.csv             .  ├── Banja Luka.csv
│   ├── Zagreb.tif            .  │   ├── Zagreb.tif                       .  │   └── Rijeka.csv            .  ├── Split.csv
│   ├── Split.csv             .  │   ├── Osijek.tif                       .  ├── Sarajevo.tif              .  ├── Rijeka.csv
│   ├── Osijek.tif            .  │   ├── Split.csv                        .  ├── Banja Luka.csv            .
│   └── Rijeka.csv            .  │   └── Rijeka.csv                       .  ├── Mostar.shp                .
  
</pre>

### STORAGE TYPE

Sorty layers based on their storage type as reported by QGIS.

Options:
  * list order of storage types of loaded layers in layer tree

#### STORAGE EXAMPLE

<pre>
TREE EXAMPLE

├── SERBIA
│   ├── Belgrade (ESRI Shapefile)
│   ├── Novi Sad (GeoJSON)
│   ├── Niš (ESRI Shapefile)
│   └── Kragujevac (GeoJSON)
├── CROATIA 
│   ├── Zagreb (SQLite)
│   ├── Osijek (SQLite)
│   ├── Split (CSV)
│   └── Rijeka (CSV)
├── Sarajevo (SQLite)
├── Banja Luka (CSV)
├── Mostar (ESRI Shapefile)
    
</pre>

<pre>

Order example:
    1.) GeoJSON
    2.) ESRI Shapefile
    3.) CSV
    4.) SQLite
    
</pre>

<pre>

          root only                .  order within all groups (root included)  .        selected group(s) only       .  extract all and sort in root
                                   .                                           .                                     .
├── Mostar (ESRI Shapefile)        .  ├── Sarajevo (SQLite)                    .  ├── SERBIA                         .  ├── Novi Sad (GeoJSON)
├── Banja Luka (CSV)               .  ├── Banja Luka (CSV)                     .  │   ├── Belgrade (ESRI Shapefile)  .  ├── Kragujevac (GeoJSON)
├── Sarajevo (SQLite)              .  ├── Mostar (ESRI Shapefile)              .  │   ├── Novi Sad (GeoJSON)         .  ├── Mostar (ESRI Shapefile)
├── SERBIA                         .  ├── SERBIA                               .  │   ├── Niš (ESRI Shapefile)       .  ├── Belgrade (ESRI Shapefile)
│   ├── Belgrade (ESRI Shapefile)  .  │   ├── Novi Sad (GeoJSON)               .  │   └── Kragujevac (GeoJSON)       .  ├── Niš (ESRI Shapefile)
│   ├── Novi Sad (GeoJSON)         .  │   ├── Kragujevac (GeoJSON)             .  ├── CROATIA (selected group)       .  ├── Banja Luka (CSV)
│   ├── Niš (ESRI Shapefile)       .  │   ├── Belgrade (ESRI Shapefile)        .  │   ├── Split (CSV)                .  ├── Rijeka (CSV)
│   └── Kragujevac (GeoJSON)       .  │   └── Niš (ESRI Shapefile)             .  │   ├── Rijeka (CSV)               .  ├── Split (CSV)
├── CROATIA                        .  ├── CROATIA                              .  │   ├── Zagreb (SQLite)            .  ├── Sarajevo (SQLite)
│   ├── Zagreb (SQLite)            .  │   ├── Split (CSV)                      .  │   └── Osijek (SQLite)            .  ├── Zagreb (SQLite)
│   ├── Osijek (SQLite)            .  │   ├── Rijeka (CSV)                     .  ├── Sarajevo (SQLite)              .  ├── Osijek (SQLite)
│   ├── Split (CSV)                .  │   ├── Zagreb (SQLite)                  .  ├── Banja Luka (CSV)               .
│   └── Rijeka (CSV)               .  │   └── Osijek (SQLite)                  .  ├── Mostar (ESRI Shapefile)        .
  
</pre>

### SIZE ON DISK

Sorts layers based on their file size on disk.

Options:
  * ascending
  * descending

*All ESRI Shapefile extensions are included in the sum when determining shapefile size.

#### SIZE ON DISK EXAMPLE

<pre>

├── SERBIA
│   ├── Belgrade (5 MB)
│   ├── Novi Sad (4 MB)
│   ├── Niš (3 MB)
│   └── Kragujevac (7 MB)
├── CROATIA
│   ├── Split (2 MB)
│   ├── Rijeka (8 MB)
│   ├── Zagreb (1 MB)
│   └── Osijek (6 MB)
├── Mostar (9 MB)
├── Banja Luka (11 MB)
├── Sarajevo (10 MB)

</pre>

<pre>
  x most to less
</pre>

<pre>

        root only          .  order within all groups (root included)  .      selected group(s) only    .  extract all and sort in root
                           .                                           .                                .
├── Banja Luka (11 MB)     .  ├── Banja Luka (11 MB)                   .  ├── SERBIA                    .  ├── Banja Luka (11 MB)
├── Sarajevo (10 MB)       .  ├── Sarajevo (10 MB)                     .  │   ├── Belgrade (5 MB)       .  ├── Sarajevo (10 MB)
├── Mostar (9 MB)          .  ├── Mostar (9 MB)                        .  │   ├── Novi Sad (4 MB)       .  ├── Mostar (9 MB)
├── SERBIA                 .  ├── SERBIA                               .  │   ├── Niš (3 MB)            .  ├── Rijeka (8 MB)
│   ├── Belgrade (5 MB)    .  │   ├── Kragujevac (7 MB)                .  │   └── Kragujevac (7 MB)     .  ├── Kragujevac (7 MB)
│   ├── Novi Sad (4 MB)    .  │   ├── Belgrade (5 MB)                  .  ├── CROATIA (selected group)  .  ├── Osijek (6 MB)
│   ├── Niš (3 MB)         .  │   ├── Novi Sad (4 MB)                  .  │   ├── Rijeka (8 MB)         .  ├── Belgrade (5 MB)
│   └── Kragujevac (7 MB)  .  │   └── Niš (3 MB)                       .  │   ├── Osijek (6 MB)         .  ├── Novi Sad (4 MB)
├── CROATIA                .  ├── CROATIA                              .  │   ├── Split (2 MB)          .  ├── Niš (3 MB)
│   ├── Split (2 MB)       .  │   ├── Rijeka (8 MB)                    .  │   └── Zagreb (1 MB)         .  ├── Split (2 MB)
│   ├── Rijeka (8 MB)      .  │   ├── Osijek (6 MB)                    .  ├── Mostar (9 MB)             .  ├── Zagreb (1 MB)
│   ├── Zagreb (1 MB)      .  │   ├── Split (2 MB)                     .  ├── Banja Luka (11 MB)        .
│   └── Osijek (6 MB)      .  │   └── Zagreb (1 MB)                    .  ├── Sarajevo (10 MB)          .
  
</pre>

### LAST MODIFIED

<pre>
          root only              .  order within all groups (root included)  .      selected group(s) only       .  extract all and sort in root
                                 .                                           .                                   .
├── SERBIA                       .  ├── Sarajevo (2024-04-06)                .  ├── SERBIA                       .  ├── Niš (2024-01-11)
│   ├── Belgrade (2024-05-30)    .  ├── Banja Luka (2024-04-22)              .  │   ├── Belgrade (2024-05-30)    .  ├── Novi Sad (2024-02-01)
│   ├── Novi Sad (2024-02-01)    .  ├── Mostar (2024-07-31)                  .  │   ├── Novi Sad (2024-02-01)    .  ├── Kragujevac (2024-03-06)
│   ├── Niš (2024-01-11)         .  ├── SERBIA                               .  │   ├── Niš (2024-01-11)         .  ├── Sarajevo (2024-04-06)
│   └── Kragujevac (2024-03-06)  .  │   ├── Niš (2024-01-11)                 .  │   └── Kragujevac (2024-03-06)  .  ├── Banja Luka (2024-04-22)
├── CROATIA                      .  │   ├── Novi Sad (2024-02-01)            .  ├── CROATIA (selected group)     .  ├── Split (2024-05-07)
│   ├── Split (2024-05-07)       .  │   └── Kragujevac (2024-03-06)          .  │   ├── Split (2024-05-07)       .  ├── Belgrade (2024-05-30) 
│   ├── Rijeka (2024-06-15)      .  │   ├── Belgrade (2024-05-30)            .  │   ├── Zagreb (2024-05-31)      .  ├── Zagreb (2024-05-31)
│   ├── Zagreb (2024-05-31)      .  ├── CROATIA                              .  │   ├── Rijeka (2024-06-15)      .  ├── Rijeka (2024-06-15)
│   └── Osijek (2024-12-02)      .  │   ├── Split (2024-05-07)               .  │   └── Osijek (2024-12-02)      .  ├── Mostar (2024-07-31)
├── Mostar (2024-07-31)          .  │   ├── Zagreb (2024-05-31)              .  ├── Mostar (2024-07-31)          .  ├── Osijek (2024-12-02)
├── Banja Luka (2024-04-22)      .  │   ├── Rijeka (2024-06-15)              .  ├── Banja Luka (2024-04-22)      .
├── Sarajevo (2024-04-06)        .  │   └── Osijek (2024-12-02)              .  ├── Sarajevo (2024-04-06)        .
  
</pre>

### POSITION

<pre>
(lat min, lat max, lon min, lon max)
  
├── EUROPE
│   ├── Croatia (42.1765993, 46.555029, 13.2104814, 19.4470842)
│   ├── Bosnia and Herzegovina (42.5553114, 45.2764135, 15.7287433, 19.6237311)
│   ├── Slovenia (45.4214242, 46.8766816, 13.3754696, 16.5967702)
│   └── Serbia (42.2322435, 46.1900524, 18.8142875, 23.006309)
├── AFRICA
│   ├── Algeria (18.968147, 37.2962055, -8.668908, 11.997337)7
│   ├── Djibouti (10.9149547, 12.7923081, 41.7713139, 43.6579046)
│   ├── Ecuador (-5.0159314, 1.8835964, -92.2072392, -75.192504)
│   └── Madagascar (-25.6071002, -11.9519693, 43.2202072, 50.4862553)
├── Dominica (15.0074207, 15.7872222, -61.6869184, -61.0329895)
├── Sri Lanka (25.2287738, 25.2303051, 55.1813071, 55.1828523)
├── Cuba (19.6275294, 23.4816972, -85.1679702, -73.9190004)
└── Mongolia (41.5800276, 52.1496, 87.73762, 119.931949)
  
</pre>

<pre>

  bottom to top

          root only             .  order within all groups (root included)  .      selected group(s) only      .  extract all and sort in root
                                .                                           .                                  .
├── Dominica                    .  ├── Dominica                             .  ├── EUROPE (selected group)     .  ├── Madagascar
├── Cuba                        .  ├── Cuba                                 .  │   ├── Bosnia and Herzegovina  .  ├── Ecuador
├── Sri Lanka                   .  ├── Sri Lanka                            .  │   ├── Serbia                  .  ├── Djibouti
├── Mongolia                    .  ├── Mongolia                             .  │   ├── Croatia                 .  ├── Dominica
├── EUROPE                      .  ├── EUROPE                               .  │   └── Slovenia                .  ├── Cuba
│   ├── Croatia                 .  │   ├── Bosnia and Herzegovina           .  ├── AFRICA                      .  ├── Sri Lanka
│   ├── Bosnia and Herzegovina  .  │   ├── Serbia                           .  │   ├── Algeria                 .  ├── Algeria
│   ├── Slovenia                .  │   ├── Croatia                          .  │   ├── Djibouti                .  ├── Bosnia and Herzegovina
│   └── Serbia                  .  │   └── Slovenia                         .  │   ├── Ecuador                 .  ├── Serbia
├── AFRICA                      .  └── AFRICA                               .  │   └── Madagascar              .  ├── Croatia
│   ├── Algeria                 .      ├── Madagascar                       .  ├── Dominica                    .  ├── Slovenia
│   ├── Djibouti                .      ├── Ecuador                          .  ├── Sri Lanka                   .  └── Mongolia
│   ├── Ecuador                 .      ├── Djibouti                         .  ├── Cuba                        .
│   └── Madagascar              .      └── Algeria                          .  └── Mongolia                    .
  
</pre>

## GROUPING

Creates groups with the layers sharing the same selected attribute(s).  
Groups are created in order of encountering unique attributes (from top to bottom).  

Options:
  * root only
  * group within all groups
  * within selected group(s)
  * extract all and group in root


### NAME

Groups layers of the same name.  
Names must match exactly.

Options:
  
  * Nodes containing same substring can be grouped together.
  
  * Groups (group names) can be ignored when grouping by name.

### GEOMETRY

Groups layers based on their geometry.

Options:
  * not all geometries have to be grouped, and option for each of the types allows you to select which ones you want to group

__NOTE__: grouping multiple geometry types in the same group is not possible.

### FEATURE COUNT

Groups layers with the same feature count.

__NOTE__: only vector layers have feature count.

### STORAGE TYPE

Groups layers with the same storage type.

__NOTE__: only vector layers have storage type.

### POSITION

Groups layers of the same extent.  

__NOTE__: Extent must match completely.

### LAST MODIFIED

Groups layers of the same last modified date.

Options:

  * day

    Group layers which have been last modified in the same day (does not mean in the last 24h).
    
  * month

    Group layers which have been last modified in the same month (does not mean within 30 days). 
  
  * year

    Group layers which have been last modified in the same year (does not mean within 1 year).

### SIZE ON DISK

Groups layers based on the provided step in megabytes.
If the step is set to 0, size on disk must match completely in order to be grouped together.

Memory layers don't have size on disk property.

All ESRI Shapefile extensions are taken into account when getting size on disk of shapefile.

### FILETYPE

Groups layers of the same filetype.


## SNAPSHOT

Snapshot is a simple copy of the current layer tree.  
Raster layers are copied by reference (absolute filepath), while for vector layers there is an option to either save by reference or by full copy of the layer attributes.  
Full vector layer copy includes layer attributes, features (feature attributes and geometry) and crs.  
Memory layers are regardless of the option for standard vector layers fully copied and saved to file.  

.snp (snapshot) file is saved in the plugin directory in /Snapshots/.

.snp files can be shared among other instances of QGIS or other PCs (supported from QGIS 3.0 version). 
As the snapshot stores an absolute path, there is no option to 'search for' or 'recover' the new filepath. 
If a load fails on some of the layers, a window containing name, type and datasource will display information of the layers that have failed to load.

Snapshot does not contain other QGIS layer properties, such as symbology and visibility.

### CREATING SNAPSHOT

* Include rasters

   If the option is ticked, raster absolute filepaths will be saved to a snapshot file.
  
* Include vector layers

  If the option is ticked, vector layers absolute filepaths will be saved to a snapshot file.
  Memory layers are fully copied and saved.

* Copy all vector layers to memory

  If the option is ticked, instead of saving the absolute filepath, layer properties and features are to a file.
  Saved properties are: layer crs, layer geometry type, layer name, layer attributes, layer features (feature attributes and feature geometry)

### LOADING SNAPSHOT

* Replace entire tree with the snapshot

   Clears entire layer tree and loads the snapshot

* Load snapshot into a separate group in root

   Loads the snapshot in newly created 'snapshot _snapshot name_' group
