package com.example.recorder;

import com.example.recorder.Trade;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Repository is an interface that provides access to data in a database
 */
public interface TradeRepo extends JpaRepository<Trade, String> {
}