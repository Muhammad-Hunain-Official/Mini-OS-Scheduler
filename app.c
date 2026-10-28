
#include <stdio.h>

#define MAX 10

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
void inputProcesses(struct Process p[], int n);
void sortByArrival(struct Process p[], int n);
void runFCFS(struct Process p[], int n,
             int order[], int start[], int end[]);
void runSJF(struct Process p[], int n,
            int order[], int start[], int end[]);
void displayResults(struct Process p[], int n);
void displayGantt(struct Process p[], int n,
                  int order[], int start[], int end[]);

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
void inputProcesses(struct Process p[], int n) {
    int i;

    for (i = 0; i < n; i++) {
        p[i].pid = i + 1;

        printf("\n--- Process P%d ---\n", p[i].pid);

        p[i].arrivalTime =
            readInt("Arrival Time (0 or greater): ", 0, 100000);

        p[i].burstTime =
            readInt("Burst Time (greater than 0): ", 1, 100000);

        p[i].priority =
            readInt("Priority (1 or greater): ", 1, 100000);

        if (p[i].arrivalTime == -1 ||
            p[i].burstTime == -1 ||
            p[i].priority == -1) {
            return;
        }
    }
}

/* Sort processes by arrival time using Bubble Sort */
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

/* First Come First Serve */
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

/* Shortest Job First - Non-Preemptive */
void runSJF(struct Process p[], int n,
            int order[], int start[], int end[]) {
    int done[MAX] = {0};
    int completed = 0;
    int currentTime = 0;
    int i, idx;

    while (completed < n) {
        idx = -1;

        /* Find the shortest available process */
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

        /* No process is available yet */
        if (idx == -1) {
            currentTime++;
            continue;
        }

        order[completed] = idx;

        if (currentTime < p[idx].arrivalTime) {
            currentTime = p[idx].arrivalTime;
        }

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

/* Display scheduling results */
void displayResults(struct Process p[], int n) {
    int i;
    float totalWT = 0;
    float totalTAT = 0;

    printf("\nPID\tAT\tBT\tCT\tTAT\tWT\n");
    printf("-----------------------------------------------\n");

    for (i = 0; i < n; i++) {
        printf("P%d\t%d\t%d\t%d\t%d\t%d\n",
               p[i].pid,
               p[i].arrivalTime,
               p[i].burstTime,
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

/* Display actual execution order and time labels */
void displayGantt(struct Process p[], int n,
                  int order[], int start[], int end[]) {
    int i;
    int currentTime = 0;

    printf("\nGANTT CHART\n");
    printf("%d", currentTime);

    for (i = 0; i < n; i++) {
        if (start[i] > currentTime) {
            printf(" -- Idle --> %d", start[i]);
        }

        printf(" -- P%d --> %d",
               p[order[i]].pid, end[i]);

        currentTime = end[i];
    }

    printf("\n");
}

/* Main program */
int main(void) {
    int i;
    struct Process p[MAX];
    int order[MAX], start[MAX], end[MAX];
    int n, choice;

    printf("===== MINI OS SCHEDULING SIMULATOR =====\n");

    n = readInt("Enter number of processes (1-10): ",
                1, MAX);

    if (n == -1) {
        return 1;
    }

    inputProcesses(p, n);

    /* Check whether input ended unexpectedly */
    for (i = 0; i < n; i++) {
        if (p[i].arrivalTime == -1 ||
            p[i].burstTime == -1 ||
            p[i].priority == -1) {
            printf("Input ended unexpectedly.\n");
            return 1;
        }
    }

    /* FCFS needs processes arranged by arrival time */
    sortByArrival(p, n);

    do {
        printf("\n===== MAIN MENU =====\n");
        printf("1. FCFS Scheduling\n");
        printf("2. SJF Scheduling\n");
        printf("3. Exit\n");

        choice = readInt("Enter your choice: ", 0, 100);

        if (choice == -1) {
            return 1;
        }

        switch (choice) {
            case 1:
                printf("\n===== FCFS RESULTS =====\n");

                runFCFS(p, n, order, start, end);
                displayResults(p, n);
                displayGantt(p, n, order, start, end);
                break;

            case 2:
                printf("\n===== SJF RESULTS =====\n");

                runSJF(p, n, order, start, end);
                displayResults(p, n);
                displayGantt(p, n, order, start, end);
                break;

            case 3:
                printf("Program ended.\n");
                break;

            default:
                printf("Invalid choice! Select 1, 2, or 3.\n");
        }

    } while (choice != 3);

    return 0;
}
