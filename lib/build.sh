mkdir -p ../src/recorder-go/_lib/
cp -r go/ ../src/recorder-go/_lib/

cd java/baggage-log-record-processor
docker build -t java-baggage-log-record-processor .
id=$(docker create java-baggage-log-record-processor)
docker cp $id:/usr/src/app/build/libs/opentelemetry-java-baggage-log-record-processor-1.0-all.jar - > ../../../src/recorder-java/_lib//opentelemetry-java-baggage-log-record-processor-all.jar
docker rm -v $id
cd ../..
# ./gradlew build
# mkdir -p ../../../src/recorder-java/_lib/
# cp build/libs/opentelemetry-java-baggage-log-record-processor-1.0-all.jar ../../../src/recorder-java/_lib/opentelemetry-java-baggage-log-record-processor-all.jar

wget -O ../src/recorder-java/_lib/elastic-otel-javaagent.jar https://repo1.maven.org/maven2/co/elastic/otel/elastic-otel-javaagent/1.0.0/elastic-otel-javaagent-1.0.0.jar

mkdir -p ../src/trader/_lib/
cp -r python/ ../src/trader/_lib/

mkdir -p ../src/monkey/_lib/
cp -r python/ ../src/monkey/_lib/