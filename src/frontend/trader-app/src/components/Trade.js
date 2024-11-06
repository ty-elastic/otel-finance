import React, { Component } from "react";
import TradeRequest from './TradeRequest'
import TradeForce from './TradeForce'

import Page from './Page'

const sections = [
  { label: 'Request Trade', desc: 'Make a trade request', element: TradeRequest },
  { label: 'Force Trade', desc: 'Force a trade ', element: TradeForce }
];

class Trade extends Component {
  render() {
    return (
      <Page sections={sections}></Page>
    );
  }
}

export default Trade;