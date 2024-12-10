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
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';

class ErrorDbRegion extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            err_db_region_on: false,
            err_db_service: 'recorder-java',
            err_db_region: 'EU'
        };

        this.monkeyState = new MonkeyState(this, 'db_error_per_region');

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
            if (this.state.err_db_region_on === false) {
                await axios.delete(`/monkey/err/db/region/${this.state.err_db_region}`);
            } else {
                await axios.post(`/monkey/err/db/region/${this.state.err_db_region}/100`,
                    null,
                    {
                        params: {
                            'err_db_service': (this.state.err_db_service === 'all') ? null : this.state.err_db_service
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

            <form name="err_db_region" onSubmit={this.handleSubmit}>
                <Grid container spacing={2}>
                    <FormControl>
                        <InputLabel id="label_region">Region</InputLabel>
                        <Select
                            labelId="label_region"
                            name="err_db_region"
                            value={this.state.err_db_region}
                            label="Region"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="EMEA">EMEA</MenuItem>
                            <MenuItem value="EU">EU</MenuItem>
                            <MenuItem value="LATAM">LATAM</MenuItem>
                            <MenuItem value="NA">NA</MenuItem>
                        </Select>
                    </FormControl>
                    <FormControl>
                        <InputLabel id="label_service">Service</InputLabel>
                        <Select
                            labelId="label_service"
                            name="err_db_service"
                            value={this.state.err_db_service}
                            label="Service"
                            onChange={this.handleInputChange}
                        >
                            <MenuItem value="all">All</MenuItem>
                            <MenuItem value="recorder-java">recorder-java</MenuItem>
                            <MenuItem value="recorder-go">recorder-go</MenuItem>
                        </Select>
                    </FormControl>
                    <FormGroup>
                        <FormControlLabel control={<Checkbox
                            name='err_db_region_on'
                            checked={this.state.err_db_region_on}
                            onChange={this.handleInputChange}
                            inputProps={{ 'aria-label': 'controlled' }}
                        />} label="Generate errors" />
                    </FormGroup>
                    <Box width="100%"><Button variant="contained" data-transaction-name="ErrorDbRegion" type="submit">Submit</Button></Box>
                    {this.monkeyState.render()}
                </Grid>
            </form>
        );
    }
}

export default ErrorDbRegion;