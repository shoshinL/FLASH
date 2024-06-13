import React, { useState, useEffect } from 'react';
import {
  decrement,
  increment,
  incrementAsync,
  incrementByAmount,
  selectCount
} from 'components/counter/counterSlice';
import { useDispatch, useSelector } from 'react-redux';

import { post } from 'utils/requests';

import styles from 'components/counter/Counter.module.scss';

export function Counter() {
  const count = useSelector(selectCount);
  const dispatch = useDispatch();
  const [incrementAmount, setIncrementAmount] = useState('2');

    // useEffect hook to perform an action when count reaches 100
  useEffect(() => {
    if (count >= 100) {
      // Perform your action here
      post(
        JSON.stringify({ number: count }),
        'double',  // This is the Flask route
        (response) => {
          alert(`Doubled number: ${response.doubledNumber}`);
        },
        (error) => {
          console.error('Failed to double the number:', error);
        }
      );
      // You could also dispatch an action, show an alert, or update the state
    }
  }, [count]);  // This effect depends on 'count', it runs whenever 'count' changes

  return (
    <div>
      <div className={ styles.row }>
        <button
          className={ styles.button }
          aria-label="Increment value"
          onClick={ () => dispatch(increment()) }
        >
          +
        </button>
        <span className={ styles.value }>{count}</span>
        <button
          className={ styles.button }
          aria-label="Decrement value"
          onClick={ () => dispatch(decrement()) }
        >
          -
        </button>
      </div>
      <div className={ styles.row }>
        <input
          className={ styles.textbox }
          aria-label="Set increment amount"
          value={ incrementAmount }
          onChange={ (e) => setIncrementAmount(e.target.value) }
        />
        <button
          className={ styles.button }
          onClick={ () =>
            dispatch(incrementByAmount(Number(incrementAmount) || 0)) }
        >
          Add Amount
        </button>
        <button
          className={ styles.asyncButton }
          onClick={ () => dispatch(incrementAsync(Number(incrementAmount) || 0)) }
        >
          Add Async
        </button>
      </div>
    </div>
  );
}
