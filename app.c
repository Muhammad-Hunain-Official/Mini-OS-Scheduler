
#include <stdio.h>

#define MAX 10
#define MAX_EVENTS 1000000

/* Large arrays for Round Robin execution history */
static int order[MAX_EVENTS];
static int start[MAX_EVENTS];
static int end[MAX_EVENTS];

struct Process {
    int pid;
    int arrivalTime;
    int burstTime;
    int priority;
    int completionTime;
    int turnaroundTime;
    int waitingTime;
};

/* Function prototypes */
int readInt(const char prompt[], int min, int max);

int inputProcesses(struct Process p[], int n);

void sortByArrival(struct Process p[], int n);

void runFCFS(struct Process p[], int n,
             int order[], int start[], int end[]);

void runSJF(struct Process p[], int n,
            int order[], int start[], int end[]);

void runPriority(struct Process p[], int n,
                 int order[], int start[], int end[]);

int runRoundRobin(struct Process p[], int n,
                  int order[], int start[], int end[],
                  int quantum);

void displayResults(struct Process p[], int n);

void displayGantt(struct Process p[],
                  int order[], int start[], int end[],
                  int eventCount);


/* Safe integer input */
int readInt(const char prompt[], int min, int max) {

    int value, ch;

    while (1) {

        printf("%s", prompt);

        if (scanf("%d", &value) != 1) {

            printf("Invalid input! Enter an integer.\n");

            while ((ch = getchar()) != '\n' && ch != EOF) {
            }

            if (ch == EOF) {
                return -1;
            }

            continue;
        }

        while ((ch = getchar()) != '\n' && ch != EOF) {
        }

        if (value < min || value > max) {

            printf("Enter a value between %d and %d.\n",
                   min, max);

            continue;
        }

        return value;
    }
}


/* Input process details */
int inputProcesses(struct Process p[], int n) {

    int i;

    for (i = 0; i < n; i++) {

        p[i].pid = i + 1;

        printf("\n--- Process P%d ---\n", p[i].pid);

        p[i].arrivalTime =
            readInt("Arrival Time (0 or greater): ", 0, 100000);

        if (p[i].arrivalTime == -1)
            return 0;

        p[i].burstTime =
            readInt("Burst Time (greater than 0): ", 1, 100000);

        if (p[i].burstTime == -1)
            return 0;

        p[i].priority =
            readInt("Priority (1 or greater): ", 1, 100000);

        if (p[i].priority == -1)
            return 0;
    }

    return 1;
}


/* Sort by Arrival Time using Bubble Sort */
void sortByArrival(struct Process p[], int n) {

    int i, j;
    struct Process temp;

    for (i = 0; i < n - 1; i++) {

        for (j = 0; j < n - 1 - i; j++) {

            if (p[j].arrivalTime > p[j + 1].arrivalTime) {

                temp = p[j];
                p[j] = p[j + 1];
                p[j + 1] = temp;
            }
        }
    }
}


/* FCFS Scheduling */
void runFCFS(struct Process p[], int n,
             int order[], int start[], int end[]) {

    int i;
    int currentTime = 0;

    for (i = 0; i < n; i++) {

        if (currentTime < p[i].arrivalTime) {
            currentTime = p[i].arrivalTime;
        }

        order[i] = i;

        start[i] = currentTime;

        currentTime += p[i].burstTime;

        end[i] = currentTime;

        p[i].completionTime = currentTime;

        p[i].turnaroundTime =
            p[i].completionTime - p[i].arrivalTime;

        p[i].waitingTime =
            p[i].turnaroundTime - p[i].burstTime;
    }
}


/* SJF Scheduling - Non-Preemptive */
void runSJF(struct Process p[], int n,
            int order[], int start[], int end[]) {

    int done[MAX] = {0};

    int completed = 0;
    int currentTime = 0;

    int i, idx;

    while (completed < n) {

        idx = -1;

        /* Find shortest available process */
        for (i = 0; i < n; i++) {

            if (done[i] == 0 &&
                p[i].arrivalTime <= currentTime) {

                if (idx == -1 ||
                    p[i].burstTime < p[idx].burstTime ||
                    (p[i].burstTime == p[idx].burstTime &&
                     p[i].arrivalTime < p[idx].arrivalTime)) {

                    idx = i;
                }
            }
        }

        /* No process available */
        if (idx == -1) {

            currentTime++;

            continue;
        }

        order[completed] = idx;

        start[completed] = currentTime;

        currentTime += p[idx].burstTime;

        end[completed] = currentTime;

        p[idx].completionTime = currentTime;

        p[idx].turnaroundTime =
            p[idx].completionTime - p[idx].arrivalTime;

        p[idx].waitingTime =
            p[idx].turnaroundTime - p[idx].burstTime;

        done[idx] = 1;

        completed++;
    }
}


/* Priority Scheduling - Non-Preemptive */
void runPriority(struct Process p[], int n,
                 int order[], int start[], int end[]) {

    int done[MAX] = {0};

    int completed = 0;
    int currentTime = 0;

    int i, idx;

    while (completed < n) {

        idx = -1;

        /* Find highest priority available process */
        for (i = 0; i < n; i++) {

            if (done[i] == 0 &&
                p[i].arrivalTime <= currentTime) {

                if (idx == -1 ||
                    p[i].priority < p[idx].priority ||
                    (p[i].priority == p[idx].priority &&
                     p[i].arrivalTime < p[idx].arrivalTime)) {

                    idx = i;
                }
            }
        }

        /* No process available */
        if (idx == -1) {

            currentTime++;

            continue;
        }

        order[completed] = idx;

        start[completed] = currentTime;

        currentTime += p[idx].burstTime;

        end[completed] = currentTime;

        p[idx].completionTime = currentTime;

        p[idx].turnaroundTime =
            p[idx].completionTime - p[idx].arrivalTime;

        p[idx].waitingTime =
            p[idx].turnaroundTime - p[idx].burstTime;

        done[idx] = 1;

        completed++;
    }
}


/* Round Robin Scheduling - Preemptive */
int runRoundRobin(struct Process p[], int n,
                  int order[], int start[], int end[],
                  int quantum) {

    int remaining[MAX];
    int queue[MAX];
    int inQueue[MAX] = {0};

    int front = 0;
    int rear = 0;
    int count = 0;

    int currentTime = 0;
    int completed = 0;

    int i, idx;
    int runTime;
    int eventCount = 0;
    int nextArrival;

    /* Initialize remaining burst times */
    for (i = 0; i < n; i++) {

        remaining[i] = p[i].burstTime;
    }

    /* Add initially available processes */
    for (i = 0; i < n; i++) {

        if (p[i].arrivalTime <= currentTime) {

            queue[rear] = i;

            rear = (rear + 1) % MAX;

            count++;

            inQueue[i] = 1;
        }
    }

    /* Execute until all processes complete */
    while (completed < n) {

        /* If ready queue is empty, find next arrival */
        if (count == 0) {

            nextArrival = -1;

            for (i = 0; i < n; i++) {

                if (remaining[i] > 0) {

                    if (nextArrival == -1 ||
                        p[i].arrivalTime < nextArrival) {

                        nextArrival = p[i].arrivalTime;
                    }
                }
            }

            currentTime = nextArrival;

            /* Add newly arrived processes */
            for (i = 0; i < n; i++) {

                if (remaining[i] > 0 &&
                    inQueue[i] == 0 &&
                    p[i].arrivalTime <= currentTime) {

                    queue[rear] = i;

                    rear = (rear + 1) % MAX;

                    count++;

                    inQueue[i] = 1;
                }
            }
        }

        /* Remove process from front of queue */
        idx = queue[front];

        front = (front + 1) % MAX;

        count--;

        inQueue[idx] = 0;

        /* Determine execution time */
        if (remaining[idx] > quantum) {

            runTime = quantum;
        }
        else {

            runTime = remaining[idx];
        }

        /* Store execution details */
        order[eventCount] = idx;

        start[eventCount] = currentTime;

        currentTime += runTime;

        remaining[idx] -= runTime;

        end[eventCount] = currentTime;

        eventCount++;

        /* Add newly arrived processes to ready queue */
        for (i = 0; i < n; i++) {

            if (i != idx &&
                remaining[i] > 0 &&
                inQueue[i] == 0 &&
                p[i].arrivalTime <= currentTime) {

                queue[rear] = i;

                rear = (rear + 1) % MAX;

                count++;

                inQueue[i] = 1;
            }
        }

        /* Check whether current process is complete */
        if (remaining[idx] == 0) {

            p[idx].completionTime = currentTime;

            p[idx].turnaroundTime =
                p[idx].completionTime - p[idx].arrivalTime;

            p[idx].waitingTime =
                p[idx].turnaroundTime - p[idx].burstTime;

            completed++;
        }

        /* Otherwise put it at the end of ready queue */
        else {

            queue[rear] = idx;

            rear = (rear + 1) % MAX;

            count++;

            inQueue[idx] = 1;
        }
    }

    return eventCount;
}


/* Display Results */
void displayResults(struct Process p[], int n) {

    int i;

    float totalWT = 0;
    float totalTAT = 0;

    printf("\nPID\tAT\tBT\tPR\tCT\tTAT\tWT\n");

    printf("-----------------------------------------------------------\n");

    for (i = 0; i < n; i++) {

        printf("P%d\t%d\t%d\t%d\t%d\t%d\t%d\n",
               p[i].pid,
               p[i].arrivalTime,
               p[i].burstTime,
               p[i].priority,
               p[i].completionTime,
               p[i].turnaroundTime,
               p[i].waitingTime);

        totalWT += p[i].waitingTime;

        totalTAT += p[i].turnaroundTime;
    }

    printf("\nAverage Waiting Time: %.2f\n",
           totalWT / n);

    printf("Average Turnaround Time: %.2f\n",
           totalTAT / n);
}


/* Display Gantt Chart */
void displayGantt(struct Process p[],
                  int order[], int start[], int end[],
                  int eventCount) {

    int i;
    int currentTime = 0;

    printf("\nGANTT CHART\n");

    printf("%d", currentTime);

    for (i = 0; i < eventCount; i++) {

        if (start[i] > currentTime) {

            printf(" -- Idle --> %d", start[i]);
        }

        printf(" -- P%d --> %d",
               p[order[i]].pid, end[i]);

        currentTime = end[i];
    }

    printf("\n");
}


/* Main Program */
int main(void) {

    struct Process p[MAX];

    int n, choice;
    int quantum;
    int eventCount;

    printf("===== MINI OS SCHEDULING SIMULATOR =====\n");

    n = readInt("Enter number of processes (1-10): ",
                1, MAX);

    if (n == -1) {
        return 1;
    }

    if (!inputProcesses(p, n)) {

        printf("Input ended unexpectedly.\n");

        return 1;
    }

    /* Sort processes by Arrival Time */
    sortByArrival(p, n);

    do {

        printf("\n===== MAIN MENU =====\n");

        printf("1. FCFS Scheduling\n");

        printf("2. SJF Scheduling\n");

        printf("3. Priority Scheduling\n");

        printf("4. Round Robin Scheduling\n");

        printf("5. Exit\n");

        choice = readInt("Enter your choice: ", 1, 5);

        if (choice == -1) {
            return 1;
        }

        eventCount = n;

        switch (choice) {

            case 1:

                printf("\n===== FCFS RESULTS =====\n");

                runFCFS(p, n, order, start, end);

                break;


            case 2:

                printf("\n===== SJF RESULTS =====\n");

                runSJF(p, n, order, start, end);

                break;


            case 3:

                printf("\n===== PRIORITY RESULTS =====\n");

                runPriority(p, n, order, start, end);

                break;


            case 4:

                printf("\n===== ROUND ROBIN RESULTS =====\n");

                quantum = readInt(
                    "Enter Time Quantum: ", 1, 100000
                );

                if (quantum == -1) {
                    return 1;
                }

                eventCount = runRoundRobin(
                    p, n, order, start, end, quantum
                );

                break;


            case 5:

                printf("Program ended.\n");

                break;


            default:

                printf("Invalid choice!\n");
        }

        if (choice >= 1 && choice <= 4) {

            displayResults(p, n);

            displayGantt(
                p, order, start, end, eventCount
            );
        }

    } while (choice != 5);

    return 0;
}
