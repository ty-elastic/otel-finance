import * as React from 'react';
import axios from "axios";

import MonkeyState from './MonkeyState'
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Grid from '@mui/material/Grid2';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Slider from '@mui/material/Slider';
import Box from '@mui/material/Box';

class Train extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            day_of_week: '',
            region: '',
            symbol: '',
            action: '',
            shares: [-1, -1],
            share_price: [-1, -1],
            classification: 'fraud'
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
            let params = {}

            if (this.state.dayOfWeek !== '') {
                params.day_of_week = this.state.day_of_week
            }
            if (this.state.region !== '') {
                params.region = this.state.region
            }
            if (this.state.symbol !== '') {
                params.symbol = this.state.symbol
            }
            if (this.state.action !== '') {
                params.action = this.state.action
            }
            if (this.state.shares[0] !== -1) {
                params.shares_min = this.state.shares[0]
            }
            if (this.state.shares[1] !== -1) {
                params.shares_max = this.state.shares[1]
            }
            if (this.state.share_price[0] !== -1) {
                params.share_price_min = this.state.share_price[0]
            }
            if (this.state.share_price[1] !== -1) {
                params.share_price_max = this.state.share_price[1]
            }

            await axios.post(`/monkey/train/${this.state.classification}`, null, {
                params: params
            });
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
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
                    <TextField
                        id="outlined-error"
                        name="symbol"
                        value={this.state.symbol}
                        onChange={this.handleInputChange}
                        label="Symbol"
                    />
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

                    <Grid size={4}>
                        <Typography gutterBottom>Shares</Typography>
                        <Slider onChange={this.handleInputChange}
                            name="shares"
                            getAriaLabel={() => "Amount"}
                            getAriaValueText={() => this.state.shares}
                            valueLabelDisplay="on"
                            shiftStep={30}
                            step={10}
                            marks
                            min={-1}
                            max={1000}
                            value={this.state.shares}
                        />
                    </Grid>
                    <Grid size={4}>
                        <Typography gutterBottom>Share Price</Typography>
                        <Slider onChange={this.handleInputChange}
                            name="share_price"
                            getAriaLabel={() => "Price"}
                            getAriaValueText={() => this.state.share_price}
                            valueLabelDisplay="on"
                            shiftStep={30}
                            step={1}
                            marks
                            min={-1}
                            max={100}
                            value={this.state.share_price}
                        />
                    </Grid>
                    <TextField
                        id="outlined-error"
                        name="classification"
                        value={this.state.classification}
                        onChange={this.handleInputChange}
                        label="Symbol"
                    />
                    <Box width="100%"><Button variant="contained" data-transaction-name="Train" type="submit">Submit</Button></Box>
                </Grid>
            </form >

        );
    }
}

export default Train;