import * as React from 'react';
import axios from "axios";
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

class ErrorReset extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    async handleSubmit(event) {
        event.preventDefault();

        try {
            await axios.post(`/monkey/reset/error`);
        } catch (err) {
            console.log(err.message)
        }
    }

    render() {
        return (

                <form name="error_reset" onSubmit={this.handleSubmit}>
                    <Stack
                    direction="column"
                    spacing={1}
                    sx={{
                        justifyContent: "flex-start",
                        alignItems: "flex-start",
                    }}
                >
                    <Button variant="contained" data-transaction-name="ErrorReset" type="submit">Reset</Button>
                </Stack>
                </form>

        );
    }
}

export default ErrorReset;