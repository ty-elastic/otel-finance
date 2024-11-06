import * as React from 'react';
import axios from "axios";

import MonkeyState from './MonkeyState'
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import FormLabel from '@mui/material/FormLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Grid from '@mui/material/Grid2';
import Button from '@mui/material/Button';
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';

class TradeForce extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            symbol: 'MOT',
            day_of_week: 'M',
            customer_id: "tb93",
            region: 'NA',
            shares: 93,
            share_price: 107.10,
            action: 'buy'
        };

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
            await axios.post("/trader/trade/force", null, {
                params: {
                    'symbol': this.state.symbol,
                    'day_of_week': this.state.day_of_week,
                    'customer_id': this.state.customer_id,
                    'region': this.state.region,
                    'action': this.state.action,
                    'shares': this.state.shares,
                    'share_price': this.state.share_price,
                    'data_source': 'customer'
                }
            });
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>

                    <TextField
                        id="outlined-error"
                        name="symbol"
                        value={this.state.symbol}
                        onChange={this.handleInputChange}
                        label="Symbol"
                    />
                    <FormControl>
                        <InputLabel id="label_dow">Day of Week</InputLabel>
                        <Select
                            labelId="label_dow"
                            name="day_of_week"
                            value={this.state.day_of_week}
                            label="Day of Week"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="M">Monday</MenuItem>
                            <MenuItem value="Tu">Tuesday</MenuItem>
                            <MenuItem value="W">Wednesday</MenuItem>
                            <MenuItem value="Th">Thursday</MenuItem>
                            <MenuItem value="F">Friday</MenuItem>
                        </Select>
                    </FormControl>
                    <TextField
                        id="outlined-error"
                        name="customer_id"
                        value={this.state.customer_id}
                        onChange={this.handleInputChange}
                        label="Customer ID"
                    />
                    <FormControl>
                        <InputLabel id="label_region">Region</InputLabel>
                        <Select
                            labelId="label_region"
                            name="region"
                            value={this.state.region}
                            label="Region"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="EMEA">EMEA</MenuItem>
                            <MenuItem value="EU">EU</MenuItem>
                            <MenuItem value="LATAM">LATAM</MenuItem>
                            <MenuItem value="NA">NA</MenuItem>
                        </Select>
                    </FormControl>
                    <Grid size={4}>
                        <Typography gutterBottom>Shares</Typography>
                        <Slider onChange={this.handleInputChange}
                            name="shares"
                            aria-label="Amount"
                            getAriaValueText={() => this.state.shares}
                            valueLabelDisplay="on"
                            shiftStep={30}
                            step={10}
                            marks
                            min={0}
                            max={10000}
                            value={this.state.shares}
                        />
                    </Grid>
                    <Grid size={4}>
                        <Typography gutterBottom>Share Price</Typography>
                        <Slider onChange={this.handleInputChange}
                            name="share_price"
                            aria-label="Share Price"
                            getAriaValueText={() => this.state.share_price}
                            valueLabelDisplay="on"
                            shiftStep={30}
                            step={1}
                            marks
                            min={0}
                            max={1000}
                            value={this.state.share_price}
                        />
                    </Grid>
                    <FormControl>
                        <InputLabel id="label_action">Action</InputLabel>
                        <Select
                            labelId="label_action"
                            name="action"
                            value={this.state.action}
                            label="Action"
                            onChange={this.handleInputChange}
                        >
                        <MenuItem value="buy">Buy</MenuItem>
                        <MenuItem value="sell">Sell</MenuItem>
                        <MenuItem value="hold">Hold</MenuItem>
                        </Select>
                    </FormControl>
                    <Box width="100%"><Button variant="contained" data-transaction-name="TradeForce" type="submit">Submit</Button></Box>
                </Grid>
            </form>
        );
    }
}

export default TradeForce;