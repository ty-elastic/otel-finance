mkdir -p ../src/recorder-go/lib/
cp -r go/* ../src/recorder-go/lib/

mkdir -p ../src/recorder-java/lib/
cd java/baggage-log-record-processor
docker build -t java-baggage-log-record-processor .
id=$(docker create java-baggage-log-record-processor)
docker cp $id:/usr/src/app/build/libs/opentelemetry-java-baggage-log-record-processor-1.0-all.jar - > ../../../src/recorder-java/lib/opentelemetry-java-baggage-log-record-processor-all.jar
docker rm -v $id
cd ../..

mkdir -p ../src/recorder-java/lib/
wget -O ../src/recorder-java/lib/elastic-otel-javaagent.jar https://repo1.maven.org/maven2/co/elastic/otel/elastic-otel-javaagent/1.0.0/elastic-otel-javaagent-1.0.0.jar

mkdir -p ../src/trader/lib/
cp -r python/* ../src/trader/lib/

mkdir -p ../src/monkey/lib/
cp -r python/* ../src/monkey/lib/