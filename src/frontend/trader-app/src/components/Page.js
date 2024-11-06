import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

export default function Page(props) {
    const [expanded, setExpanded] = React.useState('panel1');

    const handleChange = (panel) => (event, newExpanded) => {
        setExpanded(newExpanded ? panel : false);
    };

    function Element(section) {
        // Correct! JSX type can be a capitalized variable.
        const Element = section.element;
        return <Element />;
    }

    return (
        <div>
            {props.sections.map((section) => (
                <Accordion expanded={expanded === section.label} onChange={handleChange(section.label)}>
                    <AccordionSummary
                        expandIcon={<ExpandMoreIcon />}
                        aria-controls="panel2bh-content"
                        id="panel2bh-header"
                    >
                        <Typography sx={{ width: '33%', flexShrink: 0 }}>{section.label}</Typography>
                        <Typography sx={{ color: 'text.secondary' }}>
                            {section.desc}
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        {Element(section)}
                    </AccordionDetails>
                </Accordion>
            ))}
        </div>
    );
}
