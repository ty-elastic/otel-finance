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
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';

class MarketSkewMarketFactorSymbol extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            skew_market_factor_symbol_amount: 0,
            skew_market_factor_symbol: 'MOT',
        };

        this.monkeyState = new MonkeyState(this, 'skew_market_factor_per_symbol');

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
            if (this.state.skew_market_factor_symbol_amount === 0) {
                await axios.delete(`/monkey/skew_market_factor/symbol/${this.state.skew_market_factor_symbol}`);
            } else {
                await axios.post(`/monkey/skew_market_factor/symbol/${this.state.skew_market_factor_symbol}/${this.state.skew_market_factor_symbol_amount}`);
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form name="skew_market_factor_symbol" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                <Grid size={3}>
                        <Typography gutterBottom>Market Factor</Typography>
                        <Slider onChange={this.handleInputChange}
                            name="skew_market_factor_symbol_amount"
                            aria-label="Factor"
                            getAriaValueText={() => this.state.skew_market_factor_symbol_amount}
                            valueLabelDisplay="on"
                            shiftStep={30}
                            step={10}
                            marks
                            min={-100}
                            max={100}
                            value={this.state.skew_market_factor_symbol_amount}
                        />
                    </Grid>
                    <FormControl>
                        <InputLabel id="label_symbol">Symbol</InputLabel>
                        <Select
                            labelId="label_symbol"
                            name="skew_market_factor_symbol"
                            value={this.state.skew_market_factor_symbol}
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
                    <Box width="100%"><Button variant="contained" data-transaction-name="MarketSkewMarketFactorSymbol" type="submit">Submit</Button></Box>
                    {this.monkeyState.render()}
                </Grid>
            </form>
        );
    }
}

export default MarketSkewMarketFactorSymbol;