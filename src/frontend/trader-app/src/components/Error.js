import React, { useState, useEffect } from 'react';

import ErrorLatencyRegion from './ErrorLatencyRegion'
import Page from './Page'

import ErrorModelRegion from './ErrorModelRegion'
import ErrorDbRegion from './ErrorDbRegion'
import ErrorReset from './ErrorReset'
import ErrorLocal from './ErrorLocal'

const sections = [
  { label: 'Reset', desc: 'Reset error conditions', element: ErrorReset }, 
  { label: 'Browser', desc: 'Browser (Javascript) error', element: ErrorLocal },
  { label: 'Model', desc: 'Model error by region', element: ErrorModelRegion },
  { label: 'DB', desc: 'Database error by region', element: ErrorDbRegion },
  { label: 'Latency', desc: 'Latency by region', element: ErrorLatencyRegion }
];

class Error extends React.Component {
    constructor(props) {
        super(props);
        this.handleBrowserException = this.handleBrowserException.bind(this);
    }

    handleBrowserException(event) {
        throw new Error('Intentional Exception!');
    }
    render() {
        return (
          <Page sections={sections}></Page>
        );
      }
}

export default Error;
