package com.example.recorder;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import com.example.recorder.Trade;
import com.example.recorder.TradeService;
import com.example.recorder.TradeNotifier;

@RestController
@RequiredArgsConstructor
@Validated
public class TradeController {

    private final TradeService tradeService;
	private final TradeNotifier tradeNotifier;

	@GetMapping("/health")
    public ResponseEntity<String> health() {
			return ResponseEntity.ok().body("KERNEL OK");
    }

	@PostMapping("/record")
    public ResponseEntity<Trade> trade(@RequestParam(value = "customer_id") String customerId,
		@RequestParam(value = "trade_id") String tradeId,
		@RequestParam(value = "symbol") String symbol,
		@RequestParam(value = "shares") int shares,
		@RequestParam(value = "share_price") float sharePrice,
		@RequestParam(value = "action") String action) {
			Trade trade = new Trade(tradeId, customerId, symbol, shares, sharePrice, action);

			Trade resp = tradeService.recordTrade(trade);

			tradeNotifier.notify(trade);

			return ResponseEntity.ok().body(resp);
    }
}
