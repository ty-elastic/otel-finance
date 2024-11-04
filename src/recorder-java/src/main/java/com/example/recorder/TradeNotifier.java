package com.example.recorder;

import com.example.recorder.TradeRepo;
import com.example.recorder.Trade;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Service layer is where all the business logic lies
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TradeNotifier {
    private ObjectMapper mapper = new ObjectMapper();

    public void notify(Trade trade) {
        try {
            String body = mapper.writeValueAsString(trade);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI("http://notifier/notify"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(body))
                    .build();

            HttpResponse<String> response = HttpClient.newBuilder()
                    .build()
                    .send(request, BodyHandlers.ofString());
        }
        catch (Exception e) {

        }
    }
}
