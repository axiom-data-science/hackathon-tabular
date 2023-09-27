#!/bin/bash

while read path; do
  if [[ -z "$path" ]] || [[ $path == \#* ]]; then
    continue
  fi

  echo $path
  curl http://erddap-proxy:8080${path} &> /dev/null
done <<-EOF
#html dataset UI
/erddap/tabledap/cwwcNDBCMet-remote.html

#csv
/erddap/tabledap/cwwcNDBCMet-remote.csv?station%2Clongitude%2Clatitude%2Ctime%2Cwd%2Cwspd%2Cgst%2Cwvht%2Cdpd%2Capd%2Cmwd%2Cbar%2Catmp%2Cwtmp%2Cdewp%2Cvis%2Cptdy%2Ctide%2Cwspu%2Cwspv&time%3E=2023-09-20T00%3A00%3A00Z&time%3C=2023-09-27T14%3A52%3A00Z

#nc
/erddap/tabledap/cwwcNDBCMet-remote.ncCFMA?station%2Clongitude%2Clatitude%2Ctime%2Cwd%2Cwspd%2Cgst%2Cwvht%2Cdpd%2Capd%2Cmwd%2Cbar%2Catmp%2Cwtmp%2Cdewp%2Cvis%2Cptdy%2Ctide%2Cwspu%2Cwspv&time%3E=2023-09-20T00%3A00%3A00Z&time%3C=2023-09-27T14%3A52%3A00Z

#graph
/erddap/tabledap/cwwcNDBCMet-remote.graph?station%2Clongitude%2Clatitude%2Ctime%2Cwd%2Cwspd%2Cgst%2Cwvht%2Cdpd%2Capd%2Cmwd%2Cbar%2Catmp%2Cwtmp%2Cdewp%2Cvis%2Cptdy%2Ctide%2Cwspu%2Cwspv&time%3E=2023-09-20T00%3A00%3A00Z&time%3C=2023-09-27T14%3A52%3A00Z

#files
/erddap/files/cwwcNDBCMet-remote/
EOF
