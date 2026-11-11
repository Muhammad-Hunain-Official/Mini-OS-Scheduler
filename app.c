#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <ctype.h>

#define MAX_PROCESSES 100
#define MAX_EVENTS 10000

struct Process {
    int pid;
    int arrivalTime;
    int burstTime;
    int priority;
    int completionTime;
    int turnaroundTime;
    int waitingTime;
};

int ganttPID[MAX_EVENTS];
int ganttStart[MAX_EVENTS];
int ganttEnd[MAX_EVENTS];
int eventCount = 0;

/* ---------- INPUT VALIDATION ---------- */

int readInt(const char prompt[]) {
    char input[100];
    char *end;
    long value;

    while (1) {
        printf("%s", prompt);

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
    int i;


    for (i = 0; i < n; i++) {
        if (p[i].pid == id) {
            return i;
        }
    }

    return -1;
}

/* ---------- SORT BY ARRIVAL TIME ---------- */

void sortByArrival(struct Process p[], int n) {
    int i, j;


    struct Process temp;

    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - i - 1; j++) {

            if (p[j].arrivalTime > p[j + 1].arrivalTime) {
                temp = p[j];
                p[j] = p[j + 1];
                p[j + 1] = temp;
            }
        }
    }
}

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

    for (i = 0; i < n; i++) {

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
    }

    printf("\nAverage Waiting Time: %.2f",
           totalWT / n);

    printf("\nAverage Turnaround Time: %.2f\n",
           totalTAT / n);
}

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
    }

    printf("\n--- FCFS Scheduling Results ---\n");

    displayResults(p, n);
    displayGantt();
}

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
        }

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
                }
            }
        }

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

        printf("1. FCFS Scheduling\n");
        printf("2. SJF Scheduling\n");
        printf("3. Priority Scheduling\n");
        printf("4. Round Robin Scheduling\n");

        printf("\n----- Process Management -----\n");

        printf("5. Add New Process\n");
        printf("6. Update Process\n");
        printf("7. Delete Process\n");
        printf("8. Search Process\n");
        printf("9. Display All Processes\n");
        printf("10. Save Processes to File\n");
        printf("11. Load Processes from File\n");

        printf("0. Exit\n");

        choice = readInt("\nEnter Your Choice: ");

        switch (choice) {

            case 1:
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

    return 0;
}
