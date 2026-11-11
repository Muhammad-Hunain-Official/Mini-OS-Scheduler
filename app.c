#include <stdio.h>
#include <stdlib.h>
<<<<<<< HEAD

#define MAX 10
#define MAX_EVENTS 1000000

/* Gantt chart arrays */
static int order[MAX_EVENTS];
static int start[MAX_EVENTS];
static int end[MAX_EVENTS];
static int ganttChart[MAX_EVENTS][3];
=======
#include <errno.h>
#include <ctype.h>

#define MAX_PROCESSES 100
#define MAX_EVENTS 10000
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea

struct Process {
    int pid;
    int arrivalTime;
    int burstTime;
    int priority;
    int completionTime;
    int turnaroundTime;
    int waitingTime;
};

<<<<<<< HEAD
/* Function prototypes */
int readInt(const char prompt[], int min, int max);
int findProcess(struct Process p[], int n, int pid);
int inputProcesses(struct Process p[], int n);
void sortByArrival(struct Process p[], int n);
void sortByPID(struct Process p[], int n);
int binarySearch(struct Process p[], int left, int right, int pid);
void addProcess(struct Process p[], int *n);
void updateProcess(struct Process p[], int n);
void deleteProcess(struct Process p[], int *n);
void searchProcess(struct Process p[], int n);
void displayProcesses(struct Process p[], int n);
void saveProcesses(struct Process p[], int n);
void loadProcesses(struct Process p[], int *n);
void runFCFS(struct Process p[], int n, int order[], int start[], int end[]);
void runSJF(struct Process p[], int n, int order[], int start[], int end[]);
void runPriority(struct Process p[], int n, int order[], int start[], int end[]);
int runRoundRobin(struct Process p[], int n, int order[], int start[], int end[], int quantum);
void displayResults(struct Process p[], int n);
void displayGantt(struct Process p[], int order[], int start[], int end[], int eventCount);
void compareAlgorithms(struct Process p[], int n);

/* Safe integer input */
int readInt(const char prompt[], int min, int max) {
    int value, ch;
=======
int ganttPID[MAX_EVENTS];
int ganttStart[MAX_EVENTS];
int ganttEnd[MAX_EVENTS];
int eventCount = 0;

/* ---------- INPUT VALIDATION ---------- */

int readInt(const char prompt[]) {
    char input[100];
    char *end;
    long value;
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea

    while (1) {
        printf("%s", prompt);

<<<<<<< HEAD
        if (scanf("%d", &value) != 1) {
            printf("Invalid input! Enter an integer.\n");
            while ((ch = getchar()) != '\n' && ch != EOF) {
            }
            if (ch == EOF) return -1;
            continue;
        }

        while ((ch = getchar()) != '\n' && ch != EOF) {
        }

        if (value < min || value > max) {
            printf("Enter a value between %d and %d.\n", min, max);
            continue;
        }
        return value;
    }
}

/* Find process by ID */
int findProcess(struct Process p[], int n, int pid) {
    int i;
    for (i = 0; i < n; i++) {
        if (p[i].pid == pid) return i;
    }
    return -1;
}

/* Input starting processes */
int inputProcesses(struct Process p[], int n) {
=======
        if (fgets(input, sizeof(input), stdin) == NULL) {
            printf("Input error. Try again.\n");
            continue;
        }

        errno = 0;
        value = strtol(input, &end, 10);

        while (isspace((unsigned char)*end)) {
            end++;
        }

        if (end == input || *end != '\0' ||
            errno == ERANGE ||
            value < (-2147483647L - 1L) ||
            value > 2147483647L) {
            printf("Invalid input! Enter an integer.\n");
            continue;
        }

        return (int)value;
    }
}

int readPositive(const char prompt[]) {
    int value;

    do {
        value = readInt(prompt);

        if (value <= 0) {
            printf("Value must be greater than 0!\n");
        }

    } while (value <= 0);

    return value;
}

int readNonNegative(const char prompt[]) {
    int value;

    do {
        value = readInt(prompt);

        if (value < 0) {
            printf("Value cannot be negative!\n");
        }

    } while (value < 0);

    return value;
}

/* ---------- LINEAR SEARCH FOR DUPLICATE PID ---------- */

int findProcess(struct Process p[], int n, int id) {
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
    int i;


    for (i = 0; i < n; i++) {
<<<<<<< HEAD
        p[i].pid = i + 1;
        printf("\n--- Process P%d ---\n", p[i].pid);

        p[i].arrivalTime = readInt("Arrival Time (0 or greater): ", 0, 100000);
        if (p[i].arrivalTime == -1) return 0;

        p[i].burstTime = readInt("Burst Time (greater than 0): ", 1, 100000);
        if (p[i].burstTime == -1) return 0;

        p[i].priority = readInt("Priority (1 or greater): ", 1, 100000);
        if (p[i].priority == -1) return 0;
    }
    return 1;
}

/* Bubble sort by arrival time */
=======
        if (p[i].pid == id) {
            return i;
        }
    }

    return -1;
}

/* ---------- SORT BY ARRIVAL TIME ---------- */

>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
void sortByArrival(struct Process p[], int n) {
    int i, j;


    struct Process temp;

    for (i = 0; i < n - 1; i++) {
<<<<<<< HEAD
        for (j = 0; j < n - 1 - i; j++) {
=======
        for (j = 0; j < n - i - 1; j++) {

>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
            if (p[j].arrivalTime > p[j + 1].arrivalTime) {
                temp = p[j];
                p[j] = p[j + 1];
                p[j + 1] = temp;
            }
        }
    }
}

<<<<<<< HEAD
/* Bubble sort by process ID */
void sortByPID(struct Process p[], int n) {
    int i, j;
    struct Process temp;

    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - 1 - i; j++) {
            if (p[j].pid > p[j + 1].pid) {
                temp = p[j];
                p[j] = p[j + 1];
                p[j + 1] = temp;
            }
        }
    }
}

/* Recursive binary search */
int binarySearch(struct Process p[], int left, int right, int pid) {
    int mid;

    if (left > right) return -1;

    mid = (left + right) / 2;

    if (p[mid].pid == pid) return mid;
    if (pid < p[mid].pid) return binarySearch(p, left, mid - 1, pid);
    return binarySearch(p, mid + 1, right, pid);
}

/* Add a new process */
void addProcess(struct Process p[], int *n) {
    int pid;

    if (*n >= MAX) {
        printf("Process limit reached!\n");
        return;
    }

    pid = readInt("Enter new Process ID: ", 1, 100000);
    if (pid == -1) return;

    if (findProcess(p, *n, pid) != -1) {
        printf("This Process ID already exists!\n");
        return;
    }

    p[*n].pid = pid;
    p[*n].arrivalTime = readInt("Arrival Time: ", 0, 100000);
    if (p[*n].arrivalTime == -1) return;
    p[*n].burstTime = readInt("Burst Time: ", 1, 100000);
    if (p[*n].burstTime == -1) return;
    p[*n].priority = readInt("Priority: ", 1, 100000);
    if (p[*n].priority == -1) return;

    (*n)++;
    printf("Process added successfully!\n");
}

/* Update an existing process */
void updateProcess(struct Process p[], int n) {
    int pid, index;

    pid = readInt("Enter Process ID to update: ", 1, 100000);
    if (pid == -1) return;

    index = findProcess(p, n, pid);
    if (index == -1) {
        printf("Process not found!\n");
        return;
    }

    p[index].arrivalTime = readInt("New Arrival Time: ", 0, 100000);
    if (p[index].arrivalTime == -1) return;
    p[index].burstTime = readInt("New Burst Time: ", 1, 100000);
    if (p[index].burstTime == -1) return;
    p[index].priority = readInt("New Priority: ", 1, 100000);
    if (p[index].priority == -1) return;

    printf("Process updated successfully!\n");
}

/* Delete a process */
void deleteProcess(struct Process p[], int *n) {
    int pid, index, i;

    if (*n == 0) {
        printf("No processes to delete.\n");
        return;
    }

    pid = readInt("Enter Process ID to delete: ", 1, 100000);
    if (pid == -1) return;

    index = findProcess(p, *n, pid);
    if (index == -1) {
        printf("Process not found!\n");
        return;
    }

    for (i = index; i < *n - 1; i++) p[i] = p[i + 1];
    (*n)--;
    printf("Process deleted successfully!\n");
}

/* Search using recursive binary search */
void searchProcess(struct Process p[], int n) {
    struct Process temp[MAX];
    int pid, i, index;

    if (n == 0) {
        printf("No processes available.\n");
        return;
    }

    for (i = 0; i < n; i++) temp[i] = p[i];
    sortByPID(temp, n);

    pid = readInt("Enter Process ID to search: ", 1, 100000);
    if (pid == -1) return;

    index = binarySearch(temp, 0, n - 1, pid);
    if (index == -1) {
        printf("Process not found!\n");
    } else {
        printf("\nPID\tAT\tBT\tPriority\n");
        printf("%d\t%d\t%d\t%d\n", temp[index].pid,
               temp[index].arrivalTime, temp[index].burstTime,
               temp[index].priority);
    }
}

/* Display all processes */
void displayProcesses(struct Process p[], int n) {
    int i;

    if (n == 0) {
        printf("No processes available.\n");
        return;
    }

    printf("\nPID\tAT\tBT\tPriority\n");
    printf("-------------------------------\n");
    for (i = 0; i < n; i++) {
        printf("P%d\t%d\t%d\t%d\n", p[i].pid, p[i].arrivalTime,
               p[i].burstTime, p[i].priority);
    }
}

/* Save process data in a file */
void saveProcesses(struct Process p[], int n) {
    FILE *fp;
    int i;

    fp = fopen("processes.txt", "w");
    if (fp == NULL) {
        perror("Could not save file");
        return;
    }

    fprintf(fp, "%d\n", n);
    for (i = 0; i < n; i++) {
        fprintf(fp, "%d %d %d %d\n", p[i].pid, p[i].arrivalTime,
                p[i].burstTime, p[i].priority);
    }

    if (fclose(fp) != 0) {
        printf("Error while closing the file.\n");
        return;
    }
    printf("Processes saved in processes.txt successfully!\n");
}

/* Load process data from a file */
void loadProcesses(struct Process p[], int *n) {
    FILE *fp;
    struct Process temp[MAX];
    int count, i, j, duplicate;

    fp = fopen("processes.txt", "r");
    if (fp == NULL) {
        perror("Could not open file");
        return;
    }

    if (fscanf(fp, "%d", &count) != 1 || count < 0 || count > MAX) {
        printf("File data is not valid.\n");
        fclose(fp);
        return;
    }

    for (i = 0; i < count; i++) {
        if (fscanf(fp, "%d %d %d %d", &temp[i].pid,
                   &temp[i].arrivalTime, &temp[i].burstTime,
                   &temp[i].priority) != 4) {
            printf("File data is incomplete or damaged.\n");
            fclose(fp);
            return;
        }

        if (temp[i].pid <= 0 || temp[i].arrivalTime < 0 ||
            temp[i].burstTime <= 0 || temp[i].priority <= 0) {
            printf("File contains invalid process values.\n");
            fclose(fp);
            return;
        }

        duplicate = 0;
        for (j = 0; j < i; j++) {
            if (temp[j].pid == temp[i].pid) duplicate = 1;
        }
        if (duplicate) {
            printf("File contains duplicate Process IDs.\n");
            fclose(fp);
            return;
        }
    }

    fclose(fp);
    for (i = 0; i < count; i++) p[i] = temp[i];
    *n = count;
    printf("%d processes loaded successfully!\n", *n);
}

/* FCFS Scheduling */
void runFCFS(struct Process p[], int n, int order[], int start[], int end[]) {
=======
/* ---------- SORT BY PID ---------- */

void sortByPID(struct Process p[], int n) {
    int i, j;


    struct Process temp;

    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - i - 1; j++) {

            if (p[j].pid > p[j + 1].pid) {
                temp = p[j];
                p[j] = p[j + 1];
                p[j + 1] = temp;
            }
        }
    }
}

/* ---------- RECURSIVE BINARY SEARCH ---------- */

int recursiveBinarySearch(struct Process p[],
                          int low, int high, int id) {

    if (low > high) {
        return -1;
    }

    int mid = low + (high - low) / 2;

    if (p[mid].pid == id) {
        return mid;
    }

    if (id < p[mid].pid) {
        return recursiveBinarySearch(
            p, low, mid - 1, id
        );
    }

    return recursiveBinarySearch(
        p, mid + 1, high, id
    );
}

/* ---------- INITIAL INPUT ---------- */

void inputProcesses(struct Process p[], int *n) {
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
    int i;


    *n = readPositive("Enter number of processes: ");

    while (*n > MAX_PROCESSES) {
        printf("Maximum allowed processes are %d.\n",
               MAX_PROCESSES);

        *n = readPositive("Enter number of processes: ");
    }

    for (i = 0; i < *n; i++) {

        printf("\nEnter details of Process %d\n", i + 1);

        while (1) {

            p[i].pid = readPositive("Process ID: ");

            if (findProcess(p, i, p[i].pid) != -1) {
                printf("Duplicate PID! Enter another ID.\n");
            } else {
                break;
            }
        }

        p[i].arrivalTime =
            readNonNegative("Arrival Time: ");

        p[i].burstTime =
            readPositive("Burst Time: ");

        p[i].priority =
            readNonNegative("Priority: ");

        p[i].completionTime = 0;
        p[i].turnaroundTime = 0;
        p[i].waitingTime = 0;
    }

    sortByArrival(p, *n);
}

/* ---------- ADD PROCESS ---------- */

void addProcess(struct Process p[], int *n) {

    if (*n >= MAX_PROCESSES) {
        printf("\nProcess limit reached!\n");
        return;
    }

    int id;

    printf("\n--- Add New Process ---\n");

    while (1) {

        id = readPositive("Enter Process ID: ");

        if (findProcess(p, *n, id) != -1) {
            printf("This PID already exists!\n");
        } else {
            break;
        }
    }

    p[*n].pid = id;

    p[*n].arrivalTime =
        readNonNegative("Enter Arrival Time: ");

    p[*n].burstTime =
        readPositive("Enter Burst Time: ");

    p[*n].priority =
        readNonNegative("Enter Priority: ");

    p[*n].completionTime = 0;
    p[*n].turnaroundTime = 0;
    p[*n].waitingTime = 0;

    (*n)++;

    sortByArrival(p, *n);

    printf("\nProcess Added Successfully!\n");
}

/* ---------- UPDATE PROCESS ---------- */

void updateProcess(struct Process p[], int n) {

    int id;
    int index;

    printf("\n--- Update Process ---\n");

    id = readPositive("Enter Process ID to update: ");

    index = findProcess(p, n, id);

    if (index == -1) {
        printf("\nProcess Not Found!\n");
        return;
    }

    printf("\nCurrent Process Details:\n");

    printf("PID: %d\n", p[index].pid);
    printf("Arrival Time: %d\n", p[index].arrivalTime);
    printf("Burst Time: %d\n", p[index].burstTime);
    printf("Priority: %d\n", p[index].priority);

    printf("\nEnter New Details:\n");

    p[index].arrivalTime =
        readNonNegative("New Arrival Time: ");

    p[index].burstTime =
        readPositive("New Burst Time: ");

    p[index].priority =
        readNonNegative("New Priority: ");

    p[index].completionTime = 0;
    p[index].turnaroundTime = 0;
    p[index].waitingTime = 0;

    sortByArrival(p, n);

    printf("\nProcess Updated Successfully!\n");
}

/* ---------- DELETE PROCESS ---------- */

void deleteProcess(struct Process p[], int *n) {
    int i;


    int id;
    int index;

    printf("\n--- Delete Process ---\n");

    id = readPositive("Enter Process ID to delete: ");

    index = findProcess(p, *n, id);

    if (index == -1) {
        printf("\nProcess Not Found!\n");
        return;
    }

    for (i = index; i < *n - 1; i++) {
        p[i] = p[i + 1];
    }

    (*n)--;

    printf("\nProcess Deleted Successfully!\n");
}
    
/* ---------- SEARCH PROCESS USING BINARY SEARCH ---------- */

void searchProcess(struct Process p[], int n) {
    int i;


    if (n == 0) {
        printf("\nNo processes available!\n");
        return;
    }

    struct Process temp[MAX_PROCESSES];

    // Copy original process records

    for (i = 0; i < n; i++) {
        temp[i] = p[i];
    }

    // Binary Search requires PID sorted data

    sortByPID(temp, n);

    int id = readPositive("Enter Process ID to search: ");

    // Recursive Binary Search

    int index = recursiveBinarySearch(
        temp, 0, n - 1, id
    );

    if (index == -1) {
        printf("\nProcess Not Found!\n");
        return;
    }

    printf("\nProcess Found!\n");

    printf("PID: %d\n", temp[index].pid);
    printf("Arrival Time: %d\n", temp[index].arrivalTime);
    printf("Burst Time: %d\n", temp[index].burstTime);
    printf("Priority: %d\n", temp[index].priority);
}

/* ---------- DISPLAY ALL PROCESSES ---------- */

void displayProcesses(struct Process p[], int n) {
    int i;


    if (n == 0) {
        printf("\nNo processes available!\n");
        return;
    }

    printf("\nPID\tAT\tBT\tPriority\n");

    sortByArrival(p, n);

    for (i = 0; i < n; i++) {
<<<<<<< HEAD
        if (currentTime < p[i].arrivalTime) currentTime = p[i].arrivalTime;
        order[i] = i;
        start[i] = currentTime;
        currentTime += p[i].burstTime;
        end[i] = currentTime;
        p[i].completionTime = currentTime;
        p[i].turnaroundTime = p[i].completionTime - p[i].arrivalTime;
        p[i].waitingTime = p[i].turnaroundTime - p[i].burstTime;
=======

        printf("%d\t%d\t%d\t%d\n",
               p[i].pid,
               p[i].arrivalTime,
               p[i].burstTime,
               p[i].priority);
    }
}

/* ---------- GANTT CHART ---------- */

void resetGantt() {
    eventCount = 0;
}

void addEvent(int pid, int start, int end) {

    if (eventCount >= MAX_EVENTS) {
        printf("\nGantt Chart event limit reached!\n");
        return;
    }

    ganttPID[eventCount] = pid;
    ganttStart[eventCount] = start;
    ganttEnd[eventCount] = end;

    eventCount++;
}

void displayGantt() {
    int i;


    printf("\nGANTT CHART\n\n");

    if (eventCount == 0) {
        printf("No execution data available.\n");
        return;
    }

    for (i = 0; i < eventCount; i++) {

        if (ganttPID[i] == -1) {
            printf("| IDLE ");
        } else {
            printf("| P%d ", ganttPID[i]);
        }
    }

    printf("|\n");

    printf("%d", ganttStart[0]);

    for (i = 0; i < eventCount; i++) {
        printf("\t%d", ganttEnd[i]);
    }

    printf("\n");
}

/* ---------- DISPLAY RESULTS ---------- */

void displayResults(struct Process p[], int n) {
    int i;


    float totalWT = 0;
    float totalTAT = 0;

    printf("\nPID\tAT\tBT\tCT\tTAT\tWT\n");

    for (i = 0; i < n; i++) {

        p[i].turnaroundTime =
            p[i].completionTime - p[i].arrivalTime;

        p[i].waitingTime =
            p[i].turnaroundTime - p[i].burstTime;

        totalWT += p[i].waitingTime;
        totalTAT += p[i].turnaroundTime;

        printf("%d\t%d\t%d\t%d\t%d\t%d\n",
               p[i].pid,
               p[i].arrivalTime,
               p[i].burstTime,
               p[i].completionTime,
               p[i].turnaroundTime,
               p[i].waitingTime);
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
    }

    printf("\nAverage Waiting Time: %.2f",
           totalWT / n);

    printf("\nAverage Turnaround Time: %.2f\n",
           totalTAT / n);
}

<<<<<<< HEAD
/* SJF Scheduling - Non-Preemptive */
void runSJF(struct Process p[], int n, int order[], int start[], int end[]) {
    int done[MAX] = {0};
    int completed = 0, currentTime = 0;
    int i, idx, nextTime;

    while (completed < n) {
        idx = -1;
        for (i = 0; i < n; i++) {
            if (done[i] == 0 && p[i].arrivalTime <= currentTime) {
                if (idx == -1 || p[i].burstTime < p[idx].burstTime ||
                    (p[i].burstTime == p[idx].burstTime &&
                     p[i].arrivalTime < p[idx].arrivalTime)) idx = i;
            }
        }

        if (idx == -1) {
            nextTime = -1;
            for (i = 0; i < n; i++) {
                if (done[i] == 0 && (nextTime == -1 || p[i].arrivalTime < nextTime))
                    nextTime = p[i].arrivalTime;
            }
            currentTime = nextTime;
            continue;
        }

        order[completed] = idx;
        start[completed] = currentTime;
        currentTime += p[idx].burstTime;
        end[completed] = currentTime;
        p[idx].completionTime = currentTime;
        p[idx].turnaroundTime = p[idx].completionTime - p[idx].arrivalTime;
        p[idx].waitingTime = p[idx].turnaroundTime - p[idx].burstTime;
        done[idx] = 1;
        completed++;
=======
/* ---------- FCFS SCHEDULING ---------- */

void FCFS(struct Process p[], int n) {
    int i;


    if (n == 0) {
        printf("\nNo processes available!\n");
        return;
    }

    sortByArrival(p, n);
    resetGantt();

    int currentTime = 0;

    for (i = 0; i < n; i++) {

        if (currentTime < p[i].arrivalTime) {

            addEvent(-1, currentTime, p[i].arrivalTime);

            currentTime = p[i].arrivalTime;
        }

        int start = currentTime;

        currentTime += p[i].burstTime;

        p[i].completionTime = currentTime;

        addEvent(p[i].pid, start, currentTime);
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
    }

    printf("\n--- FCFS Scheduling Results ---\n");

    displayResults(p, n);
    displayGantt();
}

<<<<<<< HEAD
/* Priority Scheduling - Non-Preemptive (1 is highest priority) */
void runPriority(struct Process p[], int n, int order[], int start[], int end[]) {
    int done[MAX] = {0};
    int completed = 0, currentTime = 0;
    int i, idx, nextTime;

    while (completed < n) {
        idx = -1;
        for (i = 0; i < n; i++) {
            if (done[i] == 0 && p[i].arrivalTime <= currentTime) {
                if (idx == -1 || p[i].priority < p[idx].priority ||
                    (p[i].priority == p[idx].priority &&
                     p[i].arrivalTime < p[idx].arrivalTime)) idx = i;
            }
        }

        if (idx == -1) {
            nextTime = -1;
            for (i = 0; i < n; i++) {
                if (done[i] == 0 && (nextTime == -1 || p[i].arrivalTime < nextTime))
                    nextTime = p[i].arrivalTime;
            }
            currentTime = nextTime;
            continue;
        }

        order[completed] = idx;
        start[completed] = currentTime;
        currentTime += p[idx].burstTime;
        end[completed] = currentTime;
        p[idx].completionTime = currentTime;
        p[idx].turnaroundTime = p[idx].completionTime - p[idx].arrivalTime;
        p[idx].waitingTime = p[idx].turnaroundTime - p[idx].burstTime;
        done[idx] = 1;
        completed++;
    }
}

/* Round Robin Scheduling - Preemptive */
int runRoundRobin(struct Process p[], int n, int order[], int start[], int end[], int quantum) {
    int remaining[MAX];
    int queue[MAX];
    int inQueue[MAX] = {0};
    int front = 0, rear = 0, count = 0;
    int currentTime = 0, completed = 0;
    int i, idx, runTime, eventCount = 0, nextArrival;

    for (i = 0; i < n; i++) remaining[i] = p[i].burstTime;

    for (i = 0; i < n; i++) {
        if (p[i].arrivalTime <= currentTime) {
            queue[rear] = i;
            rear = (rear + 1) % MAX;
            count++;
            inQueue[i] = 1;
=======
/* ---------- SJF SCHEDULING ---------- */

void SJF(struct Process p[], int n) {
    int i;


    if (n == 0) {
        printf("\nNo processes available!\n");
        return;
    }

    sortByArrival(p, n);
    resetGantt();

    int completed[MAX_PROCESSES] = {0};

    int currentTime = 0;
    int count = 0;

    while (count < n) {

        int index = -1;

        for (i = 0; i < n; i++) {

            if (!completed[i] &&
                p[i].arrivalTime <= currentTime) {

                if (index == -1 ||
                    p[i].burstTime < p[index].burstTime) {

                    index = i;
                }
            }
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
        }

<<<<<<< HEAD
    while (completed < n) {
        if (count == 0) {
            nextArrival = -1;
            for (i = 0; i < n; i++) {
                if (remaining[i] > 0 &&
                    (nextArrival == -1 || p[i].arrivalTime < nextArrival))
                    nextArrival = p[i].arrivalTime;
            }
=======
        if (index == -1) {

            int nextArrival = -1;

            for (i = 0; i < n; i++) {

                if (!completed[i]) {

                    if (nextArrival == -1 ||
                        p[i].arrivalTime < nextArrival) {

                        nextArrival = p[i].arrivalTime;
                    }
                }
            }

            addEvent(-1, currentTime, nextArrival);
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
            currentTime = nextArrival;
            continue;
        }

<<<<<<< HEAD
            for (i = 0; i < n; i++) {
                if (remaining[i] > 0 && inQueue[i] == 0 &&
                    p[i].arrivalTime <= currentTime) {
                    queue[rear] = i;
                    rear = (rear + 1) % MAX;
                    count++;
                    inQueue[i] = 1;
=======
        int start = currentTime;

        currentTime += p[index].burstTime;

        p[index].completionTime = currentTime;

        completed[index] = 1;
        count++;

        addEvent(p[index].pid, start, currentTime);
    }

    printf("\n--- SJF Scheduling Results ---\n");

    displayResults(p, n);
    displayGantt();
}

/* ---------- PRIORITY SCHEDULING ---------- */

/* Lower priority number means higher priority. */

void PriorityScheduling(struct Process p[], int n) {
    int i;


    if (n == 0) {
        printf("\nNo processes available!\n");
        return;
    }

    sortByArrival(p, n);
    resetGantt();

    int completed[MAX_PROCESSES] = {0};

    int currentTime = 0;
    int count = 0;

    while (count < n) {

        int index = -1;

        for (i = 0; i < n; i++) {

            if (!completed[i] &&
                p[i].arrivalTime <= currentTime) {

                if (index == -1 ||
                    p[i].priority < p[index].priority) {

                    index = i;
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
                }
            }
        }

<<<<<<< HEAD
        idx = queue[front];
        front = (front + 1) % MAX;
        count--;
        inQueue[idx] = 0;

        if (remaining[idx] > quantum) runTime = quantum;
        else runTime = remaining[idx];

        if (eventCount >= MAX_EVENTS) {
            printf("Gantt chart limit reached.\n");
            return eventCount;
        }

        order[eventCount] = idx;
        start[eventCount] = currentTime;
        currentTime += runTime;
        remaining[idx] -= runTime;
        end[eventCount] = currentTime;
        eventCount++;

        for (i = 0; i < n; i++) {
            if (i != idx && remaining[i] > 0 && inQueue[i] == 0 &&
                p[i].arrivalTime <= currentTime) {
                queue[rear] = i;
                rear = (rear + 1) % MAX;
                count++;
                inQueue[i] = 1;
            }
        }

        if (remaining[idx] == 0) {
            p[idx].completionTime = currentTime;
            p[idx].turnaroundTime = p[idx].completionTime - p[idx].arrivalTime;
            p[idx].waitingTime = p[idx].turnaroundTime - p[idx].burstTime;
            completed++;
        } else {
            queue[rear] = idx;
            rear = (rear + 1) % MAX;
            count++;
            inQueue[idx] = 1;
        }
    }
    return eventCount;
}

/* Display CT, TAT, WT and averages */
void displayResults(struct Process p[], int n) {
    int i;
    float totalWT = 0, totalTAT = 0;

    printf("\nPID\tAT\tBT\tPR\tCT\tTAT\tWT\n");
    printf("-----------------------------------------------------------\n");
    for (i = 0; i < n; i++) {
        printf("P%d\t%d\t%d\t%d\t%d\t%d\t%d\n", p[i].pid,
               p[i].arrivalTime, p[i].burstTime, p[i].priority,
               p[i].completionTime, p[i].turnaroundTime, p[i].waitingTime);
        totalWT += p[i].waitingTime;
        totalTAT += p[i].turnaroundTime;
    }
    printf("\nAverage Waiting Time: %.2f\n", totalWT / n);
    printf("Average Turnaround Time: %.2f\n", totalTAT / n);
}

/* Display Gantt chart and use a 2D array for its values */
void displayGantt(struct Process p[], int order[], int start[], int end[], int eventCount) {
    int i;
    int currentTime = 0;

    printf("\nGANTT CHART\n");
    printf("%d", currentTime);

    for (i = 0; i < eventCount; i++) {
        ganttChart[i][0] = order[i];
        ganttChart[i][1] = start[i];
        ganttChart[i][2] = end[i];

        if (ganttChart[i][1] > currentTime)
            printf(" -- Idle --> %d", ganttChart[i][1]);

        printf(" -- P%d --> %d", p[ganttChart[i][0]].pid, ganttChart[i][2]);
        currentTime = ganttChart[i][2];
    }
    printf("\n");
}

/* Run all algorithms on copies and compare average waiting time */
void compareAlgorithms(struct Process p[], int n) {
    struct Process a[MAX], b[MAX], c[MAX], d[MAX];
    int i, events, quantum;
    float total1 = 0, total2 = 0, total3 = 0, total4 = 0;

    if (n == 0) {
        printf("No processes available.\n");
        return;
    }

    quantum = readInt("Enter Time Quantum for Round Robin: ", 1, 100000);
    if (quantum == -1) return;

    for (i = 0; i < n; i++) {
        a[i] = p[i]; b[i] = p[i]; c[i] = p[i]; d[i] = p[i];
    }

    runFCFS(a, n, order, start, end);
    for (i = 0; i < n; i++) total1 += a[i].waitingTime;

    runSJF(b, n, order, start, end);
    for (i = 0; i < n; i++) total2 += b[i].waitingTime;

    runPriority(c, n, order, start, end);
    for (i = 0; i < n; i++) total3 += c[i].waitingTime;

    events = runRoundRobin(d, n, order, start, end, quantum);
    (void)events;
    for (i = 0; i < n; i++) total4 += d[i].waitingTime;

    printf("\n===== ALGORITHM COMPARISON =====\n");
    printf("Algorithm\tAverage Waiting Time\n");
    printf("FCFS\t\t%.2f\n", total1 / n);
    printf("SJF\t\t%.2f\n", total2 / n);
    printf("Priority\t%.2f\n", total3 / n);
    printf("Round Robin\t%.2f\n", total4 / n);
}

/* Main Program */
int main(void) {
    struct Process *p;
    int n, choice, quantum, eventCount;

    /* Dynamic memory allocation */
    p = (struct Process *)malloc(MAX * sizeof(struct Process));
    if (p == NULL) {
        printf("Memory allocation failed!\n");
        return 1;
    }

    printf("===== MINI OS SCHEDULING SIMULATOR =====\n");
    n = readInt("Enter number of processes (1-10): ", 1, MAX);
    if (n == -1) {
        free(p);
        return 1;
    }

    if (!inputProcesses(p, n)) {
        printf("Input ended unexpectedly.\n");
        free(p);
        return 1;
    }

    do {
        printf("\n===== MAIN MENU =====\n");
=======
        if (index == -1) {

            int nextArrival = -1;

            for (i = 0; i < n; i++) {

                if (!completed[i]) {

                    if (nextArrival == -1 ||
                        p[i].arrivalTime < nextArrival) {

                        nextArrival = p[i].arrivalTime;
                    }
                }
            }

            addEvent(-1, currentTime, nextArrival);
            currentTime = nextArrival;
            continue;
        }

        int start = currentTime;

        currentTime += p[index].burstTime;

        p[index].completionTime = currentTime;

        completed[index] = 1;
        count++;

        addEvent(p[index].pid, start, currentTime);
    }

    printf("\n--- Priority Scheduling Results ---\n");

    displayResults(p, n);
    displayGantt();
}

/* ---------- ROUND ROBIN SCHEDULING ---------- */

void RoundRobin(struct Process p[], int n) {
    int i;


    if (n == 0) {
        printf("\nNo processes available!\n");
        return;
    }

    int quantum = readPositive("Enter Time Quantum: ");

    sortByArrival(p, n);
    resetGantt();

    int remaining[MAX_PROCESSES];
    int queue[MAX_PROCESSES];

    int front = 0;
    int rear = 0;
    int queueCount = 0;

    int currentTime = 0;
    int nextProcess = 0;
    int completed = 0;

    for (i = 0; i < n; i++) {
        remaining[i] = p[i].burstTime;
    }

    while (completed < n) {

        while (nextProcess < n &&
               p[nextProcess].arrivalTime <= currentTime) {

            queue[rear] = nextProcess;
            rear = (rear + 1) % MAX_PROCESSES;
            queueCount++;

            nextProcess++;
        }

        if (queueCount == 0) {

            if (nextProcess < n) {

                addEvent(-1, currentTime,
                         p[nextProcess].arrivalTime);

                currentTime = p[nextProcess].arrivalTime;
            }

            continue;
        }

        int index = queue[front];

        front = (front + 1) % MAX_PROCESSES;
        queueCount--;

        int start = currentTime;

        int executionTime;

        if (remaining[index] > quantum) {
            executionTime = quantum;
        } else {
            executionTime = remaining[index];
        }

        currentTime += executionTime;
        remaining[index] -= executionTime;

        addEvent(p[index].pid, start, currentTime);

        while (nextProcess < n &&
               p[nextProcess].arrivalTime <= currentTime) {

            queue[rear] = nextProcess;
            rear = (rear + 1) % MAX_PROCESSES;
            queueCount++;

            nextProcess++;
        }

        if (remaining[index] > 0) {

            queue[rear] = index;
            rear = (rear + 1) % MAX_PROCESSES;
            queueCount++;

        } else {

            p[index].completionTime = currentTime;
            completed++;
        }
    }

    printf("\n--- Round Robin Scheduling Results ---\n");

    displayResults(p, n);
    displayGantt();
}


/* ---------- FILE HANDLING: SAVE PROCESSES ---------- */

void saveProcesses(struct Process p[], int n) {
    FILE *fp;
    int i;

    fp = fopen("processes.txt", "w");

    if (fp == NULL) {
        printf("\nError: Could not open file for saving!\n");
        return;
    }

    for (i = 0; i < n; i++) {
        if (fprintf(fp, "%d %d %d %d\n",
                    p[i].pid,
                    p[i].arrivalTime,
                    p[i].burstTime,
                    p[i].priority) < 0) {
            printf("\nError while writing to file!\n");
            fclose(fp);
            return;
        }
    }

    if (fclose(fp) != 0) {
        printf("\nError while closing file!\n");
        return;
    }

    printf("\n%d process(es) saved successfully in processes.txt!\n", n);
}

/* ---------- FILE HANDLING: LOAD PROCESSES ---------- */

void loadProcesses(struct Process p[], int *n) {
    FILE *fp;
    struct Process temp[MAX_PROCESSES];
    int pid, arrival, burst, priority;
    int count = 0;
    int i;
    int duplicate;
    int scanResult;

    fp = fopen("processes.txt", "r");

    if (fp == NULL) {
        printf("\nError: processes.txt not found or could not be opened!\n");
        return;
    }

    while (1) {
        scanResult = fscanf(fp, "%d %d %d %d",
                            &pid, &arrival, &burst, &priority);

        if (scanResult == EOF) {
            break;
        }

        if (scanResult != 4) {
            printf("\nInvalid or incomplete data found in file. Loading cancelled.\n");
            fclose(fp);
            return;
        }

        if (pid <= 0 || arrival < 0 || burst <= 0 || priority < 0) {
            printf("\nInvalid process values found in file. Loading cancelled.\n");
            fclose(fp);
            return;
        }

        if (count >= MAX_PROCESSES) {
            printf("\nFile contains more than %d processes. Loading cancelled.\n",
                   MAX_PROCESSES);
            fclose(fp);
            return;
        }

        duplicate = 0;
        for (i = 0; i < count; i++) {
            if (temp[i].pid == pid) {
                duplicate = 1;
                break;
            }
        }

        if (duplicate) {
            printf("\nDuplicate PID found in file. Loading cancelled.\n");
            fclose(fp);
            return;
        }

        temp[count].pid = pid;
        temp[count].arrivalTime = arrival;
        temp[count].burstTime = burst;
        temp[count].priority = priority;
        temp[count].completionTime = 0;
        temp[count].turnaroundTime = 0;
        temp[count].waitingTime = 0;
        count++;
    }

    if (ferror(fp)) {
        printf("\nError while reading file. Loading cancelled.\n");
        fclose(fp);
        return;
    }

    fclose(fp);

    for (i = 0; i < count; i++) {
        p[i] = temp[i];
    }

    *n = count;
    sortByArrival(p, *n);

    printf("\n%d process(es) loaded successfully from processes.txt!\n", *n);
}

/* ---------- MAIN FUNCTION ---------- */

int main() {

    struct Process *p;

    int n = 0;
    int choice;

    p = (struct Process *)malloc(MAX_PROCESSES * sizeof(struct Process));

    if (p == NULL) {
        printf("Memory allocation failed!\n");
        return 1;
    }

    printf("====================================\n");
    printf("     CPU SCHEDULING SIMULATOR\n");
    printf("====================================\n");

    inputProcesses(p, &n);

    do {

        printf("\n========== MAIN MENU ==========\n");

>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea
        printf("1. FCFS Scheduling\n");
        printf("2. SJF Scheduling\n");
        printf("3. Priority Scheduling\n");
        printf("4. Round Robin Scheduling\n");
        printf("5. Add Process\n");
        printf("6. Update Process\n");
        printf("7. Delete Process\n");
        printf("8. Search Process\n");
        printf("9. Display All Processes\n");
        printf("10. Save Processes\n");
        printf("11. Load Processes\n");
        printf("12. Compare Algorithms\n");
        printf("13. Exit\n");

<<<<<<< HEAD
        choice = readInt("Enter your choice: ", 1, 13);
        if (choice == -1) {
            free(p);
            return 1;
        }
=======
        printf("\n----- Process Management -----\n");

        printf("5. Add New Process\n");
        printf("6. Update Process\n");
        printf("7. Delete Process\n");
        printf("8. Search Process\n");
        printf("9. Display All Processes\n");
        printf("10. Save Processes to File\n");
        printf("11. Load Processes from File\n");

        printf("0. Exit\n");
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea

        choice = readInt("\nEnter Your Choice: ");

        switch (choice) {
            case 1:
<<<<<<< HEAD
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
                quantum = readInt("Enter Time Quantum: ", 1, 100000);
                if (quantum == -1) {
                    free(p);
                    return 1;
                }
                eventCount = runRoundRobin(p, n, order, start, end, quantum);
                break;
            case 5:
                addProcess(p, &n);
                break;
            case 6:
                updateProcess(p, n);
                break;
            case 7:
                deleteProcess(p, &n);
                break;
            case 8:
                searchProcess(p, n);
                break;
            case 9:
                displayProcesses(p, n);
                break;
            case 10:
                saveProcesses(p, n);
                break;
            case 11:
                loadProcesses(p, &n);
                break;
            case 12:
                compareAlgorithms(p, n);
                break;
            case 13:
                printf("Program ended.\n");
                break;
        }

        if (choice >= 1 && choice <= 4) {
            displayResults(p, n);
            displayGantt(p, order, start, end, eventCount);
        }

    } while (choice != 13);
=======
                FCFS(p, n);
                break;

            case 2:
                SJF(p, n);
                break;

            case 3:
                PriorityScheduling(p, n);
                break;

            case 4:
                RoundRobin(p, n);
                break;

            case 5:
                addProcess(p, &n);
                break;

            case 6:
                updateProcess(p, n);
                break;

            case 7:
                deleteProcess(p, &n);
                break;

            case 8:
                searchProcess(p, n);
                break;

            case 9:
                displayProcesses(p, n);
                break;

            case 10:
                saveProcesses(p, n);
                break;

            case 11:
                loadProcesses(p, &n);
                break;

            case 0:
                printf("\nThank You for Using CPU Simulator!\n");
                break;

            default:
                printf("\nInvalid Choice! Try Again.\n");
        }

    } while (choice != 0);

    free(p);
>>>>>>> 1e4410894f8748f3c9c9fe6857349b83a2fc8aea

    free(p);
    return 0;
}
