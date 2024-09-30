import React, { Component } from "react";
import TradeRequest from './TradeRequest'
import TradeForce from './TradeForce'

class Trade extends Component {
  render() {
    return (
      <div>
        <h1>Make Trades</h1>

        <h2>Request Trade</h2>
        <TradeRequest/>
        <hr></hr>

        <h2>Force Trade</h2>
        <TradeForce/>
      </div>
    );
  }
}

export default Trade;