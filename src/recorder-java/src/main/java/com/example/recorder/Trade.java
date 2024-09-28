package com.example.recorder;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Column;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@NoArgsConstructor
@AllArgsConstructor
@Data
@Entity
@Table(name = "trades")
public class Trade {
  @Id
  @Column(name="trade_id")
  private String tradeId;

  @Column(name="customer_id")
  private String customerId;
  @Column(name="symbol")
  private String symbol;
  @Column(name="shares")
  private int shares;
  @Column(name="share_price")
  private float sharePrice;
  @Column(name="action")
  private String action;
}