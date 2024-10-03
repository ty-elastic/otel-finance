import React, { useState, useEffect } from 'react';

class ErrorLocal extends React.Component {
    constructor(props) {
        super(props);
        this.handleBrowserException = this.handleBrowserException.bind(this);
    }

    handleBrowserException(event) {
        throw new Error('Warning: Each child in a list should have a unique key prop');
    }

    render() {
        return (
            <div>
                <button data-transaction-name="ErrorLocal" type="submit" onClick={this.handleBrowserException} >Browser Exception</button>
            </div>
        );
    }
}

export default ErrorLocal;