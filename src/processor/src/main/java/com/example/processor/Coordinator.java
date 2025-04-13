package com.example.processor;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

public class Coordinator extends Thread {
    private static final Logger log = LoggerFactory.getLogger(Main.class);

    private String coordinatorHost;
    private String serviceName;
    private int latency;
    private boolean stop = false;

    public Coordinator(String coordinatorHost, String serviceName) {
        this.coordinatorHost = coordinatorHost;
        this.serviceName = serviceName;
        this.latency = 0;
    }

    public static Map<String, Object> convertJsonToMap(String jsonString) throws IOException {
        ObjectMapper objectMapper = new ObjectMapper();
        return objectMapper.readValue(jsonString, new TypeReference<Map<String, Object>>() {});
    }

    public int getLatency() {
        return latency;
    }

    public void shutdown() {
        this.stop = true;
    }

    @Override
    public void run() {
        while (!this.stop) {
            try {
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(new URI("http://" + this.coordinatorHost + "/latency/" + serviceName))
                        .header("Content-Type", "application/json")
                        .GET()
                        .build();

                HttpResponse<String> response = HttpClient.newBuilder()
                        .build()
                        .send(request, BodyHandlers.ofString());

                Map<String, Object> map = convertJsonToMap(response.body());
                this.latency = (int) map.get("latency");

                Thread.sleep(5000);
            }
            catch (Exception e) {
                log.error("exception", e); 
            }
        }
    }  
}
