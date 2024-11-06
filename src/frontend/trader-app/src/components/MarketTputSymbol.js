import * as React from 'react';
import axios from "axios";

import MonkeyState from './MonkeyState'
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Grid from '@mui/material/Grid2';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';

class MarketTputSymbol extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            tput_symbol_speed: 'default',
            tput_symbol: 'MOT'
        };

        this.monkeyState = new MonkeyState(this, 'high_tput_per_symbol');

        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value
        });
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {

            if (this.state.tput_symbol_speed === 'default') {
                await axios.delete(`/monkey/tput/symbol/${this.state.tput_symbol}`);
            } else {
                await axios.post(`/monkey/tput/symbol/${this.state.tput_symbol}/${this.state.tput_symbol_speed}`);
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form name="tput_symbol" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                    <FormControl>
                        <InputLabel id="label_speed">Speed</InputLabel>
                        <Select
                            labelId="label_speed"
                            name="tput_symbol_speed"
                            value={this.state.tput_symbol_speed}
                            label="Speed"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="high">High</MenuItem>
                            <MenuItem value="default">Default</MenuItem>
                        </Select>
                    </FormControl>
                    <FormControl>
                        <InputLabel id="label_region">Symbol</InputLabel>
                        <Select
                            labelId="label_region"
                            name="tput_symbol"
                            value={this.state.tput_symbol}
                            label="Symbol"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="MOT">MOT</MenuItem>
                            <MenuItem value="MSI">MSI</MenuItem>
                            <MenuItem value="GOGO">GOGO</MenuItem>
                            <MenuItem value="INTEQ">INTEQ</MenuItem>
                            <MenuItem value="VID">VID</MenuItem>
                            <MenuItem value="ESTC">ESTC</MenuItem>
                        </Select>
                    </FormControl>
                    <Box width="100%"><Button variant="contained" data-transaction-name="MarketTputSymbol" type="submit">Submit</Button></Box>
                    {this.monkeyState.render()}
                </Grid>
            </form>
        );
    }
}

export default MarketTputSymbol;