import React, { useState, useEffect } from 'react';
import Page from './Page'
import CanaryRegion from './CanaryRegion'
import TestReset from './TestReset'

const sections = [
    { label: 'Reset', desc: 'Reset test conditions', element: TestReset },
    { label: 'Canary', desc: 'Canary by region', element: CanaryRegion }
];

class Test extends React.Component {
    render() {
        return (
            <Page sections={sections}></Page>
        );
    }
}

export default Test;