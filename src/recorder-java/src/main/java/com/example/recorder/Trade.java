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

import jakarta.validation.constraints.Min;

@NoArgsConstructor
@AllArgsConstructor
@Data
@Entity
@Table(name = "trades")
public class Trade {
  @Id
  @Column(name="trade_id")
  public String tradeId;

  @Column(name="customer_id")
  public String customerId;
  @Column(name="symbol")
  public String symbol;

  @Min(value = 0, message = "shares must be > 0")
  @Column(name="shares")
  public int shares;

  @Min(value = 0, message = "share_price must be > 0")
  @Column(name="share_price")
  public float sharePrice;

  @Column(name="action")
  public String action;
}