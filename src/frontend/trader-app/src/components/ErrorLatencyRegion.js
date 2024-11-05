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

class ErrorLatencyRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            latency_region_amount: 0,
            latency_region: 'NA',
            latency_action: 'any'
        };

        this.monkeyState = new MonkeyState(this, 'latency_per_action_per_region');

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
            if (this.state.latency_region_amount === 0) {
                await axios.delete(`/monkey/latency/region/${this.state.latency_region}`);
            } else {
                await axios.post(`/monkey/latency/region/${this.state.latency_region}/${this.state.latency_region_amount}`,
                    null,
                    {
                        params: {
                            'latency_action': (this.state.latency_action === 'any') ? null : this.state.latency_action
                        }
                    }
                );
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form name="latency_region" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                    <FormControl>
                        <InputLabel id="label_region">Region</InputLabel>
                        <Select
                            labelId="label_region"
                            name="latency_region"
                            value={this.state.latency_region}
                            label="Region"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="EMEA">EMEA</MenuItem>
                            <MenuItem value="EU">EU</MenuItem>
                            <MenuItem value="LATAM">LATAM</MenuItem>
                            <MenuItem value="NA">NA</MenuItem>
                        </Select>
                    </FormControl>
                    <Grid size={3}>
                        <Typography gutterBottom>Amount (%)</Typography>
                        <Slider onChange={this.handleInputChange}
                            name="latency_region_amount"
                            aria-label="Amount (ms)"
                            getAriaValueText={() => this.state.latency_region_amount}
                            valueLabelDisplay="on"
                            shiftStep={30}
                            step={1}
                            marks
                            min={0}
                            max={1000}
                            value={this.state.latency_region_amount}
                        />
                    </Grid>
                    <FormControl>
                        <InputLabel id="label_action">Action</InputLabel>
                        <Select
                            labelId="label_action"
                            name="latency_action"
                            value={this.state.latency_action}
                            label="Action"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="any">Any</MenuItem>
                            <MenuItem value="buy">Buy</MenuItem>
                            <MenuItem value="sell">Sell</MenuItem>
                            <MenuItem value="hold">Hold</MenuItem>
                        </Select>
                    </FormControl>
                    <Button variant="contained" data-transaction-name="ErrorLatencyRegion" type="submit">Submit</Button>
                    <Box width="100%"><Paper variant="outlined">{this.monkeyState.render()}</Paper></Box>
                </Grid>
            </form>
        );
    }
}

export default ErrorLatencyRegion;