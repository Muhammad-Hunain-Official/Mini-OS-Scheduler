# Mini OS Scheduling Simulator

A console-based **CPU scheduling simulator written in C** that shows how an operating system decides which process gets the CPU and when. Enter a set of processes (arrival time, burst time, priority), pick an algorithm, and the program prints the **completion, turnaround and waiting times**, the **averages**, and a **Gantt chart** (including idle time).

An optional **Python (tkinter) GUI** with an animated Gantt chart is also included.

> **Course:** Programming Fundamentals (CT-175) - Complex Computing Activity (CCA)
> **Instructor:** Ms. Maham Ashraf
> **Semester:** Fall 2026

---

## Team Members

| S. No. | Name | Roll Number | Section |
|:------:|------|-------------|:-------:|
| 1 | Muhammad Hashim Raza | CT-26236 | E |
| 2 | Muhammad Hunain | CT-26232 | E |
| 3 | Abdul Basit | CT-26230 | E |

---

## Features

- **Four scheduling algorithms**
  - **FCFS** - First Come First Served
  - **SJF** - Shortest Job First (non-preemptive, ties broken by earlier arrival)
  - **Priority** - non-preemptive (1 = highest priority, ties broken by earlier arrival)
  - **Round Robin** - user-defined time quantum, circular queue
- **Full results for every run:** CT, TAT, WT per process, average WT and TAT, and a Gantt chart with idle periods
- **Process management:** add, update, delete, search (recursive binary search) and display processes
- **File handling:** save processes to `processes.txt` and load them back
- **Compare Algorithms:** runs all four algorithms on copies of the same data and prints the average waiting time side by side
- **Strong input validation:** letters, negative numbers and out-of-range values are rejected and asked again; the program never crashes or loops forever
- **Dynamic memory:** the process array is allocated with `malloc()` and released with `free()`

---

## Programming Concepts Used

| Concept | Where it is used |
|---------|------------------|
| Variables & data types | Time values, counters, `float` averages |
| Conditional statements | `switch` for the menu, `if / else` for validation and scheduling |
| Loops | `do-while` main menu, `while` scheduling loops, `for` input/sorting |
| Functions | ~20 functions (`readInt()`, `runFCFS()`, `runSJF()`, `runRoundRobin()`, ...) |
| Arrays | Process array, Gantt arrays, Round Robin queue |
| Structures | `struct Process` (pid, arrival, burst, priority, CT, TAT, WT) |
| Pointers / dynamic memory | `malloc()` / `free()`, `int *n` parameters |
| File handling | `fopen()`, `fprintf()`, `fclose()`, `perror()` |
| Recursion | `binarySearch()` |
| Sorting & searching | Bubble sort (by arrival / PID) + recursive binary search |

---

## Project Structure

```
Mini-OS-Scheduler/
|-- app.c              # Main C program (console simulator)
|-- gui.py             # Optional Python tkinter GUI
|-- processes.txt      # Sample / saved process data
|-- Flowchart.pdf      # Program flowchart
|-- Project_Report.pdf # Full project report
`-- README.md
```

---

## Getting Started

### Run the C program

**Requirements:** a C compiler such as GCC.

```bash
# Compile
gcc app.c -o app

# Run (Linux / macOS)
./app

# Run (Windows)
app.exe
```

### Run the GUI (optional)

**Requirements:** Python 3 with tkinter (included in the standard installation, no extra packages needed).

```bash
python gui.py
```

The GUI offers three themes (Aurora / Sunset / Daylight), an animated Gantt chart, step mode and hover tooltips. Press **F5** to run.

---

## How to Use

1. Enter the **number of processes** (1 to 10).
2. For each process, enter **Arrival Time** (0 or more), **Burst Time** (1 or more) and **Priority** (1 or more).
3. Choose an option from the main menu:

```
===== MAIN MENU =====
1.  FCFS Scheduling
2.  SJF Scheduling
3.  Priority Scheduling
4.  Round Robin Scheduling
5.  Add Process
6.  Update Process
7.  Delete Process
8.  Search Process
9.  Display All Processes
10. Save Processes
11. Load Processes
12. Compare Algorithms
13. Exit
```

### `processes.txt` format

The first line is the number of processes, then one line per process: `PID ArrivalTime BurstTime Priority`.

```
4
1 0 6 2
2 2 8 1
3 4 3 3
4 20 4 2
```

---

## Sample Output

Using the sample data above:

| Algorithm | Avg. Waiting Time | Avg. Turnaround Time | Gantt Chart |
|-----------|:-----------------:|:--------------------:|-------------|
| FCFS | 3.50 | 8.75 | `0 -- P1 --> 6 -- P2 --> 14 -- P3 --> 17 -- Idle --> 20 -- P4 --> 24` |
| SJF | 2.25 | 7.50 | `0 -- P1 --> 6 -- P3 --> 9 -- P2 --> 17 -- Idle --> 20 -- P4 --> 24` |
| Priority | 3.50 | 8.75 | `0 -- P1 --> 6 -- P2 --> 14 -- P3 --> 17 -- Idle --> 20 -- P4 --> 24` |
| Round Robin (q = 3) | 3.75 | 9.00 | `0 -- P1 --> 3 -- P2 --> 6 -- P1 --> 9 -- P3 --> 12 -- P2 --> 15 -- P2 --> 17 -- Idle --> 20 -- P4 --> 23 -- P4 --> 24` |

**Formulas used**

- Turnaround Time (TAT) = Completion Time (CT) - Arrival Time (AT)
- Waiting Time (WT) = Turnaround Time (TAT) - Burst Time (BT)

---

## Testing

The program was tested with valid, invalid and boundary inputs, including:

- Non-numeric input (`abc`), zero, negative and out-of-range values
- Invalid menu choices
- All four scheduling algorithms (including CPU idle time)
- Add / update / delete / search with duplicate and missing IDs
- Saving to a file and comparing all algorithms

All test cases passed. See `Project_Report.pdf` for the full test table and screenshots.

---

## Future Improvements

- Add preemptive algorithms such as **Shortest Remaining Time First (SRTF)**
- Replace the fixed limit of 10 processes with a dynamically growing list

---

## License

This project was developed for academic purposes as part of Programming Fundamentals (CT-175).
