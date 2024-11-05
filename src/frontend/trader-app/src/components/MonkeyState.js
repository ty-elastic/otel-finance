import React, { useState, useEffect } from 'react';
import axios from "axios";

class MonkeyState {
    constructor(parent, key) {
        this.parent = parent;
        this.key = key;

        this.parent.state.data = null;
        this.fetchData();
    }

    fetchData() {
        axios.get('/monkey/state')
            .then(response => {
                this.parent.setState({ data: response.data });
                console.log(response.data);
            })
            .catch(error => {
                // Handle error
                console.error(error);
            });
    }

    render() {
        return (
            <div align="left">
                {/* Render your component based on the data */}
                {this.parent.state.data ? (
                    <pre style={{ fontFamily: 'monospace' }}>{JSON.stringify(this.parent.state.data[this.key], null, 2)}</pre>
                ) : (
                    <pre style={{ fontFamily: 'monospace' }}>loading...</pre>
                )}
            </div>
        );
    }
}

export default MonkeyState;
