import React, { useState, useEffect } from 'react';

import ErrorLatencyRegion from './ErrorLatencyRegion'
import CanaryRegion from './CanaryRegion'

import ErrorModelRegion from './ErrorModelRegion'
import ErrorDbRegion from './ErrorDbRegion'
import ErrorReset from './ErrorReset'
import ErrorLocal from './ErrorLocal'

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
            <div>
                <h1>Generate Errors</h1>

                <h2>Reset Conditions</h2>
                <ErrorReset></ErrorReset>
                <hr></hr>

                <h2>Browser (Javascript) Error</h2>
                <ErrorLocal/>
                <hr></hr>

                <h2>Model Error by Region</h2>
                <ErrorModelRegion/>
                <hr></hr>

                <h2>DB Error by Region</h2>
                <ErrorDbRegion/>
                <hr></hr>

                <h2>Latency by Region</h2>
                <ErrorLatencyRegion/>
                <hr></hr>

                <h2>Canary by Region</h2>
                <CanaryRegion/>
                <hr></hr>

            </div>




        );
    }
}

export default Error;