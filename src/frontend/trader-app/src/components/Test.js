import React, { useState, useEffect } from 'react';

import CanaryRegion from './CanaryRegion'
import TestReset from './TestReset'

class Test extends React.Component {
    constructor(props) {
        super(props);
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

export default Test;