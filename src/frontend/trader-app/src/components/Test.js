import React, { useState, useEffect } from 'react';

import CanaryRegion from './CanaryRegion'
import TestReset from './TestReset'

class Error extends React.Component {
    constructor(props) {
        super(props);
        this.handleBrowserException = this.handleBrowserException.bind(this);
    }

    render() {
        return (
            <div>
                <h1>Generate Tests</h1>

                <h2>Reset Conditions</h2>
                <TestReset></TestReset>
                <hr></hr>

                <h2>Canary by Region</h2>
                <CanaryRegion/>
                <hr></hr>
            </div>
        );
    }
}

export default Error;