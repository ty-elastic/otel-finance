import React, { Component } from "react";
import TrainClassification from './TrainClassification'

import Page from './Page'

const sections = [
  { label: 'Classification', desc: 'Train Classification', element: TrainClassification }
];

class Train extends Component {
  render() {
    return (
      <Page sections={sections}></Page>
    );
  }
}

export default Train;