import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { Fragment } from 'react';

interface Props {
  names: string[];
  data: JSX.Element[] | undefined;
}

export default function TableTemplate({ names, data }: Props) {
  const skeletonRows = 10;

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label='table'>
        <TableHead>
          <TableRow>
            {names.map((name, i) => (
              <TableCell key={i}>{name}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data
            ? data.map((row, i) => <Fragment key={i}>{row}</Fragment>)
            : [...Array(skeletonRows)].map((v, i) => (
                <TableRow key={i}>
                  {names.map((name, i) => (
                    <TableCell key={i}>
                      <Skeleton />
                    </TableCell>
                  ))}
                </TableRow>
              ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
