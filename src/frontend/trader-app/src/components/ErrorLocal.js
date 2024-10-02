import React, { useState, useEffect } from 'react';

class ErrorLocal extends React.Component {
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
                <button data-transaction-name="ErrorLocal" type="submit" onClick={this.handleBrowserException} >Browser Exception</button>
            </div>
        );
    }
}

export default ErrorLocal;