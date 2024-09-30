import React, { useState, useEffect } from 'react';

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
                <h1>Generate Local Errors</h1>

                <h2>Javascript Exception</h2>
                <button type="submit" onClick={this.handleBrowserException} >Browser Exception</button>
            </div>
        );
    }
}

export default Error;