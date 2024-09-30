FROM maven:3-eclipse-temurin-17 AS build  

WORKDIR /usr/src/app

COPY src ./src

COPY build.gradle .
COPY gradle ./gradle
COPY gradlew .
COPY gradlew.bat .
COPY gradle.properties .
COPY settings.gradle .

RUN ./gradlew build
