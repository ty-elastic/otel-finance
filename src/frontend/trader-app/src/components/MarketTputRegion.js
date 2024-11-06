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

class MarketTputRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            tput_region_speed: 'default',
            tput_region: 'NA',
        };

        this.monkeyState = new MonkeyState(this, 'high_tput_per_region');

        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        console.log(target.name)

        this.setState({
            [name]: value
        });
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            if (this.state.tput_region_speed === 'default') {
                await axios.delete(`/monkey/tput/region/${this.state.tput_region}`);
            } else {
                await axios.post(`/monkey/tput/region/${this.state.tput_region}/${this.state.tput_region_speed}`);
            }
            this.monkeyState.fetchData();
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (
            <form name="tput_region" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                    <FormControl>
                        <InputLabel id="label_speed">Speed</InputLabel>
                        <Select
                            labelId="label_speed"
                            name="tput_region_speed"
                            value={this.state.tput_region_speed}
                            label="Speed"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="high">High</MenuItem>
                            <MenuItem value="default">Default</MenuItem>
                        </Select>
                    </FormControl>
                    <FormControl>
                        <InputLabel id="label_region">Region</InputLabel>
                        <Select
                            labelId="label_region"
                            name="tput_region"
                            value={this.state.tput_region}
                            label="Region"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="EMEA">EMEA</MenuItem>
                            <MenuItem value="EU">EU</MenuItem>
                            <MenuItem value="LATAM">LATAM</MenuItem>
                            <MenuItem value="NA">NA</MenuItem>
                        </Select>
                    </FormControl>
                    <Box width="100%"><Button variant="contained" data-transaction-name="MarketTputRegion" type="submit">Submit</Button></Box>
                    {this.monkeyState.render()}
                </Grid>
            </form>
        );
    }
}

export default MarketTputRegion;