# declarations.com.ua

#### Useful links

* Design: https://github.com/ArialBlack/Decl.in.ua
* Form to digitize scanned declarations: https://github.com/dimanech/form
* Our crowdsourcing framework that'll be used to crowdsource digitization process: https://github.com/mrgambal/vulyk
* Assorted scripts to cleanup data: https://github.com/dchaplinsky/open-declaration

#### R pre-requisites to generate analytics
First of all install ```R 3.1``` or newer

then run ```R``` and install following packages:
* ```install.packages('devtools')```
* ```require(devtools)```
* ```install_version("knitr", version = "1.10", repos = "http://cran.us.r-project.org")```
* ```install_version("ggplot2", version = "1.0.1", repos = "http://cran.us.r-project.org")```
* ```install_version("knitrBootstrap", version = "0.9.0", repos = "http://cran.us.r-project.org")```
* ```install.packages('dplyr')```
* ```install_version("xtable", version = "1.7-4", repos = "http://cran.us.r-project.org")```
* ```install_version("scales", version = "0.2.4", repos = "http://cran.us.r-project.org")```
* ```install_version("doBy", version = "4.5-13", repos = "http://cran.us.r-project.org")```


#### Running locally with Docker

It's possible to utilise docker and docker-compose to run declarations.com.ua locally. Everything except R analytics
should work with it at the time of writing this.

**WARNING: This is currently not suitable for production as is. Web service should not run with `runserver` and various settings should be altered.**

First make sure you have recent Docker CE (tested on 17.03.1) and docker-compose (tested on 1.13.0), then follow these
steps from the repository root:
1. Make sure git submodules are pulled in
2. docker-compose up -d
3. docker-compose run --rm web python3 manage.py migrate
4. (optional) docker-compose run --rm web python3 manage.py createsuperuser
5. docker-compose run --rm web python3 manage.py createindices declarations_v2 nacp_declarations

In order to import NACP data:
1. Create a `declarations_bank` directory in the repo root (don't worry, it's gitignored)
2. Visit `http://localhost:5984/_utils/` and go to "Setup" tab in order to create CouchDB stuff
3. docker-compose run dragnet_utils python3 load.py /mnt/declarations_bank/your_nacp_archive_dir -u admin -p admin -e http://couchdb:5984 -c 15 -C 200 -S /mnt/declarations_bank/laststate

Choose params according to [dragnet](https://github.com/excieve/dragnet) documentation.

In order to run dragnet execution profiles:
docker-compose run --rm dragnet_utils python3 profile.py aggregated all -d /mnt/dragnet_data -u admin -p admin -e http://couchdb:5984 -E http://elasticsearch:9200

This should also pump the latest data to ElasticSearch, provided the state file is where the profile expects it to be.

See dragnet repo for more details about it. `--noreexport` param might be needed in case of recurring execution (such as a cron job).


You may use `/mnt/declarations_bank` volume for other import dumps as well and remap to a different host path if needed.

If everything's good then the site should be available at `http://localhost:8000/` and CouchDB admin .

This setup also includes a container to work with elasticdump, which can be invoked with `docker-compose run elasticdump`.
