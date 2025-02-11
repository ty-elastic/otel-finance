FROM mcr.microsoft.com/dotnet/sdk:8.0

# install OpenTelemetry .NET Automatic Instrumentation
# ARG OTEL_VERSION=1.8.0
# ADD https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/releases/download/v${OTEL_VERSION}/otel-dotnet-auto-install.sh otel-dotnet-auto-install.sh
# RUN apt-get update && apt-get install -y unzip && \
#     OTEL_DOTNET_AUTO_HOME="/otel-dotnet-auto" sh otel-dotnet-auto-install.sh

WORKDIR /app
COPY *.cs .
COPY Services .
COPY appsettings.json .
COPY *.csproj .
RUN dotnet publish -c Release -o out

# enable OpenTelemetry .NET Automatic Instrumentation
# ENV CORECLR_ENABLE_PROFILING="1"
# ENV CORECLR_PROFILER='{918728DD-259F-4A6A-AC2B-B85E1B658318}'
# ENV CORECLR_PROFILER_PATH="/otel-dotnet-auto/linux-x64/OpenTelemetry.AutoInstrumentation.Native.so"
# ENV DOTNET_ADDITIONAL_DEPS="/otel-dotnet-auto/AdditionalDeps"
# ENV DOTNET_SHARED_STORE="/otel-dotnet-auto/store"
# ENV DOTNET_STARTUP_HOOKS="/otel-dotnet-auto/net/OpenTelemetry.AutoInstrumentation.StartupHook.dll"
# ENV OTEL_DOTNET_AUTO_HOME="/otel-dotnet-auto"

ENV OTEL_SERVICE_NAME="notifier"
ENV OTEL_EXPERIMENTAL_RESOURCE_DETECTORS="process_runtime"
ENV OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES="Notifier"
ENV OTEL_DOTNET_AUTO_METRICS_ADDITIONAL_SOURCES="Notifier"

ENTRYPOINT [ "./out/Notifier", "--urls", "http://*:5000" ]