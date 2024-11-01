import React, { useState, useEffect } from 'react';
import axios from "axios";

class State extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: null,
        };
        this.key = props.key;
    }

    async updateState() {
        try {
            let response = await axios.get('/monkey/state')
            this.server_state = response[this.key]
        } catch (err) {
            console.log(err.message)
        }
    }
    componentDidMount() {
        // This code runs once after the component is mounted
        // Similar to useEffect(() => {}, [])
    }

    componentDidUpdate(prevProps, prevState) {
        // This code runs after each render when props or state changes
        // Similar to useEffect(() => {}, [dependency])
        this.updateState();
    }

    componentWillUnmount() {
        // This code runs right before the component is unmounted
        // Similar to the cleanup function in useEffect
    }

    render() {
        return (
            <div>
                {/* Render your component based on the data */}
                {this.state.data ? (
                <pre>{JSON.stringify(this.server_state, null, 2)}</pre>
                ) : (
                <p>loading...</p>
                )}
            </div>
        );
    }
}

export default State;
