package com.example.recorder;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import com.example.recorder.Trade;
import com.example.recorder.TradeService;

@RestController
@RequiredArgsConstructor
@Validated
public class TradeController {

    private final TradeService tradeService;

	@PostMapping("/record")
    public ResponseEntity<Trade> trade(@RequestParam(value = "customer_id") String customerId,
		@RequestParam(value = "trade_id") String tradeId,
		@RequestParam(value = "symbol") String symbol,
		@RequestParam(value = "shares") int shares,
		@RequestParam(value = "share_price") float sharePrice,
		@RequestParam(value = "action") String action) {
			Trade trade = new Trade(customerId, tradeId, symbol, shares, sharePrice, action);
			return ResponseEntity.ok().body(tradeService.recordTrade(trade));
    }
}
