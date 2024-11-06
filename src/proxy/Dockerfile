ARG NGINX_VERSION=1.26.0

FROM nginx:${NGINX_VERSION}

ARG OTEL_MODULE_VERSION=1.1.0

RUN apt-get update ; apt-get install unzip
ADD https://github.com/open-telemetry/opentelemetry-cpp-contrib/releases/download/webserver/v${OTEL_MODULE_VERSION}/opentelemetry-webserver-sdk-x64-linux.tgz /opt/opentelemetry-webserver-sdk-x64-linux.tgz
RUN cd /opt ; tar xvfz opentelemetry-webserver-sdk-x64-linux.tgz
RUN cd /opt/opentelemetry-webserver-sdk; ./install.sh
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/opentelemetry-webserver-sdk/sdk_lib/lib
RUN echo "load_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so;\n$(cat /etc/nginx/nginx.conf)" > /etc/nginx/nginx.conf
COPY opentelemetry_module.conf /etc/nginx/conf.d

COPY default.conf /etc/nginx/conf.d/default.conf
COPY cors.conf /etc/nginx/cors.conf

