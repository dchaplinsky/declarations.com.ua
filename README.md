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

**WARNING: This is currently not suitable for production.**

First make sure you have recent Docker CE (tested on 17.03.1) and docker-compose (tested on 1.13.0), then follow these
steps from the repository root:
1. docker-compose up -d
2. docker-compose run web python3 manage.py migrate
3. (optional) docker-compose run web python3 manage.py createsuperuser
4. docker-compose run web python3 manage.py createindices declarations_v2 nacp_declarations
5. Run any data import as required similarly to previous steps

If everything's good then the site should be available at `http://localhost:8000/`.

This setup also includes a container to work with elasticdump, which can be invoked with `docker-compose run elasticdump`.
