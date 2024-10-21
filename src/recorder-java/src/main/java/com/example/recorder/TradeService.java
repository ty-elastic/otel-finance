package com.example.recorder;

import com.example.recorder.TradeRepo;
import com.example.recorder.Trade;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Service layer is where all the business logic lies
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TradeService {

    private final TradeRepo tradeRepo;

    public Trade recordTrade (Trade trade){
        Trade savedTrade = tradeRepo.save(trade);

        // intentionally make this slow to compare to go variant
        try {
            Thread.sleep(10);
        }
        catch (Exception e) {}

        log.info("trade committed for " + trade.customerId);
        return savedTrade;
    }
}
