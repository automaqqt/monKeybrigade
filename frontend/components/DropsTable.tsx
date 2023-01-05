import Button from '@mui/material/Button';
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import axios from 'axios';
import humanizeDuration from "humanize-duration";
import useSWR from 'swr';
import Link from '../src/Link';
import TableTemplate from './TableTemplate';

function getTypeNamed(type: string) {
  if (type == "mining") {
    return "Raffle"
  }
  if (type == "targetmining") {
    return "Target mining"
  }
}
export default function DropsTable() {
  const { data: drops } = useSWR<DropsApiResponse, Error>(
    ['https://taco.api.cryptomonkeys.cc/drops', { params: { before: '', after: '' } }],
    (url, options) => axios.get(url, options).then((res) => res.data),
    { refreshInterval: 60000, }
  );

  return (
    <>
      <TableTemplate
        names={['When?', 'Type', 'Winner', 'Status', 'Transaction']}
        data={drops?.data.map((row, i) => (
          <TableRow key={i} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
            <TableCell>{humanizeDuration(Date.now() - Date.parse(row.issue_time + "Z"), { round: true, conjunction: " and " })} ago</TableCell>
            <TableCell>{getTypeNamed(row.type)}</TableCell>
            <TableCell>{row.winners.join(", ")}</TableCell>
            <TableCell>{row.state}</TableCell>
            <TableCell>
              <Link sx={{ textDecoration: 'none' }} href={`https://wax.bloks.io/transaction/${row.trx_id}`}>
                <Button variant='outlined'>bloks.io</Button>
              </Link>
            </TableCell>
          </TableRow>
        ))}
      />
    </>
  );
}
