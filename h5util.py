"""Basic utility functions for working with h5 files"""
import h5py
import numpy as np
import logging

import argparse



def collect_virtual_dataset(output_file, input_file_list, output_dataset_name, input_dataset_name):
  total_shape, cols = _get_final_shape(input_file_list)
  layout = h5py.VirtualLayout(shape=total_shape, dtype=np.float64)
  j=0
  with h5py.File(output_file, 'a') as f:
    for i, file in enumerate(input_file_list):
      logging.info(f'Processing {file}')
      vsource = h5py.VirtualSource(file, input_dataset_name, shape=(total_shape[0], cols[i]))
      layout[:, j:j+cols[i]] = vsource
      j += cols[i]
    f.create_virtual_dataset(output_dataset_name, layout, fillvalue=0.0)
  pass


def _get_final_shape(file_list):
  with h5py.File(file_list[0], 'r') as f:
    n0 = f['data'].shape[0]
  total_cols = 0
  cols = []
  for file in file_list:
    with h5py.File(file, 'r') as f:
      fshape = f['data'].shape
      assert fshape[0] == n0, 'inconsistent shape'
      assert len(fshape) == 2, 'only 2D data supported'
      cols.append(fshape[1])
      total_cols += fshape[1]
  return (n0, total_cols), cols


def convert_npy_to_h5(input_file, output_file, out_shape=None):
  data = np.load(input_file)
  if out_shape is not None:
    out_shape = data.shape
  with h5py.File(output_file, 'w') as f:
    f.create_dataset('data', data=np.reshape(data, out_shape))


def collect_and_reshape(input_file, output_file, data_fields, out_shape):
  """
  Collects data_fields from input_file, vstacks, and then reshapes them to out_shape
  The result is saved in output_file
  """
  with h5py.File(input_file, 'r') as f:
    d = []
    for datafield in data_fields:
      print('datafield shape %s', f[datafield].shape)
      d.append(np.reshape(np.array(f[datafield]), out_shape))
    A = np.vstack(d)
  with h5py.File(output_file, 'w') as f:
    f.create_dataset('data', data=A)


def transpose(input_files, output_files, input_dataset_name='data', output_dataset_name='data'):
  for input_file, output_file in zip(input_files, output_files):
    with h5py.File(input_file, 'r') as f:
      A = np.array(f[input_dataset_name])
    with h5py.File(output_file, 'w') as f:
      f.create_dataset(output_dataset_name, data=A.T)


def separate(input_file, output_files, data_fields, chunk_limit=-1):
  with h5py.File(input_file, 'r') as f:
    for output_file, datafield in zip(output_files, data_fields):
      A = np.array(f[datafield][:, :chunk_limit])
      with h5py.File(output_file, 'w') as g:
        g.create_dataset('data', data=A)


def matrix_collection(input_files, output_files, data_fields, idcs, out_shape, i_start, slice):
  for input_file, output_file, datafield in zip(input_files, output_files, data_fields):
    for idx in idcs:
      data_point = np.array(h5py.File(input_file, 'r')[datafield][i_start:np.prod(out_shape)+i_start, idx])
      data_point = np.reshape(data_point, out_shape)
      if len(out_shape) == 3:
        data_point = data_point[:, :, slice]
      np.savetxt(f'{output_file}-{idx}.txt', data_point)


def extract_field(input_file, output_file, datafield):
  with h5py.File(input_file, 'r') as f:
    A = np.array(f[datafield])
    np.save(output_file, A)
  pass


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('function', type=str, help='Function to run')
  parser.add_argument('--input_files', type=str, nargs='+')
  parser.add_argument('--output_files', type=str, nargs='+')
  parser.add_argument('--data_fields', type=str, nargs='+')
  parser.add_argument('--out_shape', type=int, nargs='+')
  parser.add_argument('--chunk_limit', type=int)
  parser.add_argument('--idcs', type=int, nargs='+')
  parser.add_argument('--i_start', type=int, default=0)
  parser.add_argument('--slice', type=int, default=0)
  args = parser.parse_args()
  if args.function == 'collect_virtual_dataset':
    collect_virtual_dataset(args.output_files[0], args.input_files, args.data_fields[0], args.data_fields[1])
  elif args.function == 'convert_npy_to_h5':
    for input_file, output_file in zip(args.input_files, args.output_files):
      convert_npy_to_h5(input_file, output_file)
  elif args.function == 'collect_and_reshape':
    for input_file, output_file in zip(args.input_files, args.output_files):
      collect_and_reshape(input_file, output_file, args.data_fields, args.out_shape)
  elif args.function == 'transpose':
    transpose(args.input_files, args.output_files)
  elif args.function == 'separate':
    separate(args.input_files[0], args.output_files, args.data_fields, args.chunk_limit)
  elif args.function == 'matrix_collection':
    matrix_collection(args.input_files, args.output_files, args.data_fields, args.idcs, args.out_shape, args.i_start, args.slice)
  elif args.function == 'extract_field':
    extract_field(args.input_files[0], args.output_files[0], args.data_fields[0])
  else:
    raise ValueError('Function not found')


if __name__ == '__main__':
  main()



